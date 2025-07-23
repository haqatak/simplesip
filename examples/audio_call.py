#!/usr/bin/env python3
"""
Audio Call Example - SimpleSIP

This example demonstrates how to make a SIP call with audio streaming
using SimpleSIP and PyAudio for microphone/speaker support.
"""

from simplesip import SimpleSIPClient
import time
import sys
import threading
import numpy as np

try:
    import pyaudio
except ImportError:
    print("❌ PyAudio is required for audio support")
    print("Install with: pip install pyaudio")
    sys.exit(1)

class AudioCallHandler:
    def __init__(self, username, password, server):
        self.client = SimpleSIPClient(username, password, server)
        
        # Audio configuration
        self.CHUNK = 160  # 20ms at 8kHz (160 samples)
        self.FORMAT = pyaudio.paInt16  # 16-bit samples
        self.CHANNELS = 1  # Mono
        self.RATE = 8000   # 8kHz sample rate for PCMU
        
        # Audio objects
        self.audio = None
        self.input_stream = None
        self.output_stream = None
        
        # Threading
        self.audio_thread_running = False
        self.audio_thread = None
        
        # Set up audio callback
        self.client.set_audio_callback(self.on_audio_received, format='pcmu')
    
    def on_audio_received(self, audio_data, format):
        """Handle incoming audio from remote party"""
        if format == 'pcmu' and self.output_stream:
            try:
                # Convert μ-law to PCM for playback
                pcm_data = self.ulaw_to_pcm(audio_data)
                
                # Play audio through speakers
                if not self.output_stream._stopped:
                    self.output_stream.write(pcm_data)
                    
            except Exception as e:
                print(f"Audio playback error: {e}")
    
    def ulaw_to_pcm(self, ulaw_data):
        """Convert μ-law audio to 16-bit PCM"""
        ulaw_samples = np.frombuffer(ulaw_data, dtype=np.uint8)
        
        # μ-law decompression algorithm
        ulaw_samples = ulaw_samples ^ 0xFF  # Complement all bits
        sign = (ulaw_samples & 0x80) != 0
        exponent = (ulaw_samples & 0x70) >> 4
        mantissa = ulaw_samples & 0x0F
        
        # Calculate linear value
        linear = ((mantissa.astype(np.int32) << 3) + 0x84) << exponent
        linear = np.where(sign, -linear, linear)
        
        # Clamp to 16-bit range
        linear = np.clip(linear, -32768, 32767)
        
        return linear.astype(np.int16).tobytes()
    
    def pcm_to_ulaw(self, pcm_data):
        """Convert 16-bit PCM to μ-law"""
        pcm_samples = np.frombuffer(pcm_data, dtype=np.int16)
        
        # μ-law compression algorithm
        BIAS = 0x84
        CLIP = 32635
        
        ulaw_samples = []
        for sample in pcm_samples:
            # Get sign and absolute value
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
    
    def setup_audio(self):
        """Initialize PyAudio and audio streams"""
        try:
            self.audio = pyaudio.PyAudio()
            
            # Input stream (microphone)
            self.input_stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            # Output stream (speakers)
            self.output_stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True,
                frames_per_buffer=self.CHUNK
            )
            
            print(f"🎤 Audio initialized - {self.RATE}Hz, {self.CHANNELS} channel(s)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize audio: {e}")
            return False
    
    def cleanup_audio(self):
        """Stop and cleanup audio streams"""
        self.audio_thread_running = False
        
        if self.audio_thread:
            self.audio_thread.join(timeout=2)
        
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            
        if self.audio:
            self.audio.terminate()
            
        print("🛑 Audio cleanup completed")
    
    def audio_thread_func(self):
        """Thread function for capturing and sending audio"""
        try:
            while self.audio_thread_running and self.client.running:
                if self.client.call_state.value in ['connected', 'streaming']:
                    try:
                        # Read audio from microphone
                        data = self.input_stream.read(self.CHUNK, exception_on_overflow=False)
                        
                        # Convert PCM to μ-law
                        ulaw_data = self.pcm_to_ulaw(data)
                        
                        # Send via RTP
                        self.client.send_audio(ulaw_data)
                        
                    except Exception as e:
                        if self.audio_thread_running:
                            print(f"Audio capture error: {e}")
                            break
                
                time.sleep(0.02)  # 20ms intervals
                
        except Exception as e:
            print(f"Audio thread error: {e}")
    
    def start_audio_thread(self):
        """Start the audio capture thread"""
        self.audio_thread_running = True
        self.audio_thread = threading.Thread(target=self.audio_thread_func, daemon=True)
        self.audio_thread.start()
        print("🎵 Audio streaming started")
    
    def make_call_with_audio(self, destination):
        """Make a call with full audio support"""
        try:
            print("SimpleSIP - Audio Call Example")
            print("=" * 40)
            
            # Setup audio first
            if not self.setup_audio():
                return False
            
            # Connect to SIP server
            print(f"📡 Connecting to SIP server...")
            if not self.client.connect():
                print("❌ Failed to connect to SIP server")
                return False
            
            print("✅ Connected to SIP server")
            
            # Make the call
            print(f"📞 Calling {destination}...")
            if not self.client.make_call(destination):
                print("❌ Failed to initiate call")
                return False
            
            print("📤 Call initiated, waiting for response...")
            
            # Wait for call to connect
            timeout = 30
            start_time = time.time()
            
            while self.client.call_state.value not in ['connected', 'streaming']:
                if time.time() - start_time > timeout:
                    print("⏰ Call timeout")
                    return False
                    
                if self.client.call_state.value == 'idle':
                    print("❌ Call failed or rejected")
                    return False
                    
                print(f"📋 Call state: {self.client.call_state.value}")
                time.sleep(1)
            
            # Call connected - start audio
            print("✅ Call connected with audio streaming!")
            print("🎤 Speak into your microphone")
            print("🔊 Audio will be played through speakers")
            print("Press Ctrl+C to end the call")
            
            # Start audio streaming
            self.start_audio_thread()
            
            # Keep call active until interrupted
            try:
                while self.client.running and self.client.call_state.value != 'idle':
                    # Print status every 10 seconds
                    status = self.client.get_call_status()
                    print(f"📊 Status: {status['state']} | RTP: {status['remote_rtp']} | Buffer: {status['audio_buffer_size']}")
                    time.sleep(10)
                    
            except KeyboardInterrupt:
                print("\n🛑 Call interrupted by user")
            
            return True
            
        except Exception as e:
            print(f"❌ Call error: {e}")
            return False
            
        finally:
            # Cleanup
            print("🔚 Ending call...")
            self.client.end_call()
            self.cleanup_audio()
            self.client.disconnect()
            print("👋 Call ended")

def main():
    # Configuration - Update with your details
    USERNAME = "1001"
    PASSWORD = "your_password"
    SERVER = "192.168.1.100"
    DESTINATION = "1002"
    
    if len(sys.argv) > 1:
        DESTINATION = sys.argv[1]
    
    # Create call handler
    handler = AudioCallHandler(USERNAME, PASSWORD, SERVER)
    
    # Make call with audio
    success = handler.make_call_with_audio(DESTINATION)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())