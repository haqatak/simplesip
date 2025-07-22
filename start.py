# from bridge.server import BetterSIPCall
from bridge.sdk import BetterSIPClient
import time
import threading
import struct
import numpy as np
try:
    import pyaudio
except ImportError:
    print("Please install pyaudio: pip install pyaudio")
    exit(1)


client = BetterSIPClient("1004", "ba5cc9c1a2b8632caf467b326e9e27e6", "10.128.50.210")

# Audio configuration
CHUNK = 160  # 20ms at 8kHz (160 samples)
FORMAT = pyaudio.paInt16  # 16-bit samples
CHANNELS = 1  # Mono
RATE = 8000   # 8kHz sample rate for PCMU

# Global variables
audio = None
stream = None
audio_thread_running = False


def audio_capture_thread():
    """Thread to capture audio from microphone and send via RTP"""
    global audio_thread_running
    
    try:
        while audio_thread_running and client.running:
            if client.call_state.value in ['connected', 'streaming']:
                # Read audio data from microphone
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Convert to PCMU (μ-law) format
                # pyaudio gives us 16-bit linear PCM, convert to μ-law
                pcmu_data = pcm_to_ulaw(data)
                
                # Send via RTP
                client.send_audio(pcmu_data)
                
            time.sleep(0.02)  # 20ms intervals
            
    except Exception as e:
        print(f"Audio capture error: {e}")
        
def start_audio_capture():
    """Initialize and start audio capture"""
    global audio, stream, audio_thread_running
    
    try:
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Open microphone stream
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print(f"🎤 Microphone initialized - {RATE}Hz, {CHANNELS} channel(s)")
        
        # Start audio capture thread
        audio_thread_running = True
        audio_thread = threading.Thread(target=audio_capture_thread, daemon=True)
        audio_thread.start()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize microphone: {e}")
        return False
        
def stop_audio_capture():
    """Stop audio capture and cleanup"""
    global audio, stream, audio_thread_running
    
    audio_thread_running = False
    
    if stream:
        stream.stop_stream()
        stream.close()
        
    if audio:
        audio.terminate()
        
    print("🛑 Audio capture stopped")

def pcm_to_ulaw(pcm_data):
    """Convert 16-bit linear PCM to μ-law (PCMU) format"""
    # Convert bytes to numpy array of 16-bit integers
    pcm_samples = np.frombuffer(pcm_data, dtype=np.int16)
    
    # μ-law compression algorithm
    # Bias and scale
    BIAS = 0x84
    CLIP = 32635
    
    ulaw_samples = []
    for sample in pcm_samples:
        # Get absolute value and apply bias
        sign = 0x80 if sample < 0 else 0x00
        if sample < 0:
            sample = -sample
        if sample > CLIP:
            sample = CLIP
        sample += BIAS
        
        # Find the position of the highest set bit
        exp = 7
        while exp > 0 and sample < (0x1 << (exp + 7)):
            exp -= 1
        
        # Calculate mantissa
        mantissa = (sample >> (exp + 3)) & 0x0F
        
        # Combine sign, exponent, and mantissa
        ulaw_byte = sign | (exp << 4) | mantissa
        ulaw_samples.append(ulaw_byte ^ 0xFF)  # Complement all bits
    
    return bytes(ulaw_samples)

try:
    # Connect to SIP server
    client.connect()
    
    # Initialize audio capture
    if not start_audio_capture():
        print("Failed to start audio capture")
        exit(1)
    
    # Make the call
    print("📞 Making call to 1002...")
    client.make_call("1002")
    
    # Wait for call to be established
    print("⏳ Waiting for call to connect...")
    while client.call_state.value not in ['connected', 'streaming'] and client.running:
        time.sleep(0.1)
    
    if client.call_state.value in ['connected', 'streaming']:
        print("✅ Call connected! Audio streaming started.")
        print("🎤 Speak into your microphone - audio will be transmitted")
        print("Press Ctrl+C to end the call")
    
    # Keep the call active
    while client.running and client.call_state.value != 'idle':
        # Print call status every 10 seconds
        status = client.get_call_status()
        print(f"📊 Status: {status['state']} | RTP: {status['remote_rtp']} | Buffer: {status['audio_buffer_size']}")
        time.sleep(10)
        
except KeyboardInterrupt:
    print("\n🛑 Stopping call...")
    stop_audio_capture()
    client.disconnect()
except Exception as e:
    print(f"❌ Error: {e}")
    stop_audio_capture()
    client.disconnect()
