# from bridge.server import BetterSIPCall
from simplesip import SimpleSIPClient
import time
import threading
import struct
import numpy as np
try:
    import pyaudio
except ImportError:
    print("Please install pyaudio: pip install pyaudio")
    exit(1)


client = SimpleSIPClient("1004", "ba5cc9c1a2b8632caf467b326e9e27e6", "10.128.50.210")

# Audio configuration - adaptive based on negotiated codec
CHUNK = 160  # 20ms at 8kHz (160 samples) - will adjust for G.722
FORMAT = pyaudio.paInt16  # 16-bit samples
CHANNELS = 1  # Mono
RATE = 8000   # 8kHz sample rate for PCMU/PCMA - will adjust for G.722

# Global variables
audio = None
stream = None
audio_thread_running = False


def audio_capture_thread():
    """Thread to capture audio from microphone and send via RTP"""
    global audio_thread_running
    
    try:
        packet_count = 0
        while audio_thread_running and client.running:
            if client.call_state.value in ['connected', 'streaming']:
                # Read audio data from microphone
                data = stream.read(CHUNK, exception_on_overflow=False)
                
                # Monitor audio levels and quality periodically
                packet_count += 1
                if packet_count % 50 == 0:  # Every ~1 second
                    import numpy as np
                    samples = np.frombuffer(data, dtype=np.int16)
                    rms = np.sqrt(np.mean(samples**2))
                    db = 20 * np.log10(rms) if rms > 0 else -60
                    peak = np.max(np.abs(samples))
                    print(f"🎤 Audio: {db:.1f}dB (RMS: {rms:.0f}, Peak: {peak}, Size: {len(data)} bytes)")
                    
                    # Check for clipping
                    if peak > 30000:
                        print("⚠️  Audio clipping detected - reduce microphone volume")
                
                # Send PCM data directly - client will handle codec encoding
                # based on negotiated codec (G.722, PCMU, or PCMA)
                client.send_audio(data)
                
            time.sleep(0.02)  # 20ms intervals
            
    except Exception as e:
        print(f"Audio capture error: {e}")
        
def start_audio_capture():
    """Initialize and start audio capture with adaptive sample rate"""
    global audio, stream, audio_thread_running, RATE, CHUNK
    
    try:
        # Wait for codec negotiation if call is in progress
        if hasattr(client, 'call_state') and client.call_state.value != 'idle':
            # Wait a bit for codec negotiation
            for _ in range(20):  # 2 second timeout
                if client.negotiated_codec:
                    break
                time.sleep(0.1)
        
        # Adjust audio parameters based on negotiated codec
        if client.negotiated_codec == 'G722':
            RATE = 16000
            CHUNK = 320  # 20ms at 16kHz
            print(f"🎵 Configuring for G.722: {RATE}Hz, {CHUNK} samples")
        else:
            RATE = 8000  
            CHUNK = 160  # 20ms at 8kHz
            print(f"🎵 Configuring for PCMU/PCMA: {RATE}Hz, {CHUNK} samples")
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Open microphone stream with correct parameters
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


try:
    # Connect to SIP server
    client.connect()
    
    # Make the call first to negotiate codec
    print("📞 Making call to 1002...")
    client.make_call("1002")
    
    # Wait for call to be established and codec negotiated
    print("⏳ Waiting for call to connect and negotiate codec...")
    while client.call_state.value not in ['connected', 'streaming'] and client.running:
        time.sleep(0.1)
    
    if client.call_state.value in ['connected', 'streaming']:
        print("✅ Call connected! Setting up audio with correct sample rate...")
        print(f"🎵 Negotiated codec: {client.negotiated_codec}")
        
        # Initialize audio capture AFTER codec negotiation
        if not start_audio_capture():
            print("Failed to start audio capture")
            exit(1)
            
        print("🎤 Speak into your microphone - audio will be transmitted")
        print("Press Ctrl+C to end the call")
    
    # Keep the call active
    while client.running and client.call_state.value != 'idle':
        # Print call status every 10 seconds
        status = client.get_call_status()
        codec_info = f" | Codec: {client.negotiated_codec}" if client.negotiated_codec else ""
        print(f"📊 Status: {status['state']} | RTP: {status['remote_rtp']} | Buffer: {status['audio_buffer_size']}{codec_info}")
        time.sleep(10)
        
except KeyboardInterrupt:
    print("\n🛑 Stopping call...")
    stop_audio_capture()
    client.disconnect()
except Exception as e:
    print(f"❌ Error: {e}")
    stop_audio_capture()
    client.disconnect()
