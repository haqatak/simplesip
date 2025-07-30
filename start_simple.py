#!/usr/bin/env python3
"""
Simplified SIP audio client - automatic codec handling
The client automatically detects and handles both PCMU and G.722 codecs
"""

from simplesip import SimpleSIPClient
import time
import threading
import pyaudio

client = SimpleSIPClient("1001", "ba5cc9c1a2b8632caf467b326e9e27e6", "10.128.50.210")
audio = None
input_stream = None
output_stream = None
running = False
audio_queue = []

# Audio format (will be dynamically configured by client)
FORMAT = pyaudio.paInt16
CHANNELS = 1

def list_microphones():
    """List available microphones and let user choose"""
    audio = pyaudio.PyAudio()
    
    print("\n🎤 Available Microphones:")
    print("-" * 50)
    
    input_devices = []
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:  # Input device
            input_devices.append((i, info))
            print(f"{len(input_devices)}. {info['name']} (Device {i})")
            print(f"   Channels: {info['maxInputChannels']}, Rate: {info['defaultSampleRate']}")
    
    audio.terminate()
    
    if not input_devices:
        print("❌ No input devices found!")
        return None
    
    print("-" * 50)
    while True:
        try:
            choice = input(f"Choose microphone (1-{len(input_devices)}) or Enter for default: ").strip()
            if not choice:
                return None  # Use default
            
            idx = int(choice) - 1
            if 0 <= idx < len(input_devices):
                device_id, device_info = input_devices[idx]
                print(f"✅ Selected: {device_info['name']}")
                return device_id
            else:
                print(f"❌ Please enter 1-{len(input_devices)}")
        except ValueError:
            print("❌ Please enter a number")
        except KeyboardInterrupt:
            return None

def audio_receive_callback(audio_data, format_type, play_time=None, codec=None):
    """Callback for received audio - client automatically handles codec decoding"""
    global audio_queue
    
    if format_type == 'pcm':
        # Client has already decoded the audio to PCM
        audio_queue.append(audio_data)

def audio_playback_thread():
    """Thread to play received audio"""
    global running, audio_queue
    
    while running:
        if audio_queue and output_stream:
            try:
                pcm_data = audio_queue.pop(0)
                output_stream.write(pcm_data)
            except Exception as e:
                print(f"Playback error: {e}")
        else:
            time.sleep(0.01)  # Short sleep when no audio

def audio_capture_thread():
    """Audio capture - client automatically handles codec encoding"""
    global running
    
    while running and client.running:
        if client.call_state.value in ['connected', 'streaming']:
            try:
                # Get audio config from client
                config = client.get_audio_config()
                chunk_size = config['chunk_size']
                
                # Read audio from microphone
                pcm_data = input_stream.read(chunk_size, exception_on_overflow=False)
                
                # Send to client - it will automatically encode based on negotiated codec
                client.send_audio(pcm_data)
                    
            except Exception as e:
                print(f"Audio capture error: {e}")
                
        time.sleep(0.02)  # 20ms

def setup_audio_streams(mic_device_id=None):
    """Setup audio streams using client's audio configuration"""
    global audio, input_stream, output_stream
    
    # Get audio configuration from client
    config = client.get_audio_config()
    rate = config['sample_rate']
    chunk_size = config['chunk_size']
    
    print(f"🎵 Setting up audio streams:")
    print(f"   Codec: {config['codec']}")
    print(f"   Sample Rate: {rate}Hz")
    print(f"   Chunk Size: {chunk_size} samples")
    
    # Initialize audio
    audio = pyaudio.PyAudio()
    
    # Open input stream (microphone)
    input_kwargs = {
        'format': FORMAT,
        'channels': CHANNELS, 
        'rate': rate,
        'input': True,
        'frames_per_buffer': chunk_size
    }
    
    if mic_device_id is not None:
        input_kwargs['input_device_index'] = mic_device_id
        
    input_stream = audio.open(**input_kwargs)
    
    # Open output stream (speakers)
    output_stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=rate,
        output=True,
        frames_per_buffer=chunk_size
    )

try:
    print("🔊 SimpleSIP Audio Client - Automatic Codec Handling")
    print("Connecting...")
    
    # Connect and register
    client.connect()
    time.sleep(2)
    
    # Make call
    print("📞 Calling 1002...")
    client.make_call("1002")
    
    # Wait for connection
    while client.call_state.value not in ['connected', 'streaming'] and client.running:
        time.sleep(0.1)
    
    if client.call_state.value in ['connected', 'streaming']:
        # Get negotiated codec information
        config = client.get_audio_config()
        print(f"✅ Connected with {config['codec']} codec")
        
        if config['codec'] == 'G722':
            print("🎉 High-quality wideband audio active!")
        else:
            print(f"📻 Using {config['codec']} codec")
        
        # Choose microphone
        mic_device_id = list_microphones()
        
        # Set up audio callback for receiving (client handles codec decoding)
        client.set_audio_callback(audio_receive_callback, 'g722')
        
        # Setup audio streams with correct configuration
        setup_audio_streams(mic_device_id)
        
        print("🎤 Audio started - you can now talk and hear!")
        print("💡 Client automatically handles codec encoding/decoding")
        
        # Start audio threads
        running = True
        capture_thread = threading.Thread(target=audio_capture_thread, daemon=True)
        playback_thread = threading.Thread(target=audio_playback_thread, daemon=True)
        
        capture_thread.start()
        playback_thread.start()
        
        # Keep running
        while client.running and client.call_state.value != 'idle':
            time.sleep(1)
            
except KeyboardInterrupt:
    print("\n🛑 Stopping...")
finally:
    running = False
    if input_stream:
        input_stream.close()
    if output_stream:
        output_stream.close()
    if audio:
        audio.terminate()
    client.disconnect()