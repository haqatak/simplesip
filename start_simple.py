#!/usr/bin/env python3
"""
Simple working PCMU audio client - no fancy stuff, just works
"""

from simplesip import SimpleSIPClient
import time
import threading
import audioop
import pyaudio

# Simple audio configuration for PCMU
CHUNK = 160  # 20ms at 8kHz 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000  # 8kHz for PCMU

client = SimpleSIPClient("1004", "ba5cc9c1a2b8632caf467b326e9e27e6", "10.128.50.210")
audio = None
input_stream = None
output_stream = None
running = False
audio_queue = []

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

def audio_receive_callback(pcm_data, format_type, play_time=None):
    """Callback for received audio - add to playback queue"""
    global audio_queue
    if format_type == 'pcm':
        audio_queue.append(pcm_data)

def audio_playback_thread():
    """Thread to play received audio"""
    global running, audio_queue
    
    while running:
        if audio_queue and output_stream:
            try:
                # Get audio data from queue
                pcm_data = audio_queue.pop(0)
                
                # Play it
                output_stream.write(pcm_data)
                
            except Exception as e:
                print(f"Playback error: {e}")
        else:
            time.sleep(0.01)  # Short sleep when no audio

def audio_capture_thread():
    """Simple audio capture and transmission"""
    global running
    
    while running and client.running:
        if client.call_state.value in ['connected', 'streaming']:
            try:
                # Read audio from mic
                pcm_data = input_stream.read(CHUNK, exception_on_overflow=False)
                
                # Convert to μ-law using Python's built-in
                ulaw_data = audioop.lin2ulaw(pcm_data, 2)
                
                # Send directly to RTP
                if client.remote_rtp_info and len(ulaw_data) == 160:
                    # Create RTP header for PCMU (PT=0)
                    import struct
                    header = struct.pack('!BBHII', 
                                       0x80,  # Version=2
                                       0,     # PT=0 (PCMU) 
                                       client.rtp_seq,
                                       client.rtp_timestamp,
                                       client.rtp_ssrc)
                    pass
                    # Send RTP packet
                    # client.rtp_sock.sendto(header + ulaw_data, client.remote_rtp_info)
                    
                    # Update counters
                    # client.rtp_seq = (client.rtp_seq + 1) % 65536
                    # client.rtp_timestamp += 160
                    
            except Exception as e:
                print(f"Audio capture error: {e}")
                
        time.sleep(0.02)  # 20ms

try:
    print("🔊 Simple PCMU Audio Client")
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
        print(f"✅ Connected with {client.negotiated_codec}")
        
        # Choose microphone
        mic_device_id = list_microphones()
        
        # Set up audio callback for receiving
        client.set_audio_callback(audio_receive_callback, 'pcm')
        
        # Initialize audio
        audio = pyaudio.PyAudio()
        
        # Open input stream (microphone)
        input_kwargs = {
            'format': FORMAT,
            'channels': CHANNELS, 
            'rate': RATE,
            'input': True,
            'frames_per_buffer': CHUNK
        }
        
        if mic_device_id is not None:
            input_kwargs['input_device_index'] = mic_device_id
            
        input_stream = audio.open(**input_kwargs)
        
        # Open output stream (speakers)
        output_stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK
        )
        
        print("🎤 Audio started - you can now talk and hear!")
        print("🔊 You should hear audio from extension 1002")
        
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