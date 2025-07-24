Examples
========

This page contains practical examples of using SimpleSIP.

Basic Call Example
------------------

Simple outbound call:

.. code-block:: python

    from simplesip import SimpleSIPClient
    import time
    
    def basic_call_example():
        client = SimpleSIPClient("1001", "password", "192.168.1.100")
        
        try:
            print("Connecting...")
            client.connect()
            time.sleep(2)  # Wait for registration
            
            print("Making call...")
            client.make_call("1002")
            
            # Wait for connection
            while client.call_state.value != 'connected':
                if client.call_state.value == 'idle':
                    print("Call failed")
                    return
                time.sleep(0.1)
                
            print("Call connected!")
            input("Press Enter to hang up...")
            
        finally:
            client.disconnect()
    
    if __name__ == "__main__":
        basic_call_example()

Audio Streaming Example  
-----------------------

Full duplex audio streaming:

.. code-block:: python

    from simplesip import SimpleSIPClient
    import pyaudio
    import threading
    import time
    import audioop
    
    class AudioCallClient:
        def __init__(self, username, password, server):
            self.client = SimpleSIPClient(username, password, server)
            self.audio = None
            self.input_stream = None
            self.output_stream = None
            self.running = False
            
            # Audio config
            self.CHUNK = 160
            self.FORMAT = pyaudio.paInt16
            self.CHANNELS = 1
            self.RATE = 8000
            
        def audio_callback(self, pcm_data, format_type):
            """Handle received audio"""
            if self.output_stream and format_type == 'pcm':
                self.output_stream.write(pcm_data)
                
        def audio_capture_thread(self):
            """Capture and send audio"""
            while self.running:
                if self.client.call_state.value in ['connected', 'streaming']:
                    try:
                        # Read from microphone
                        pcm_data = self.input_stream.read(self.CHUNK, 
                                                        exception_on_overflow=False)
                        
                        # Send audio
                        self.client.send_audio(pcm_data)
                        
                    except Exception as e:
                        print(f"Audio error: {e}")
                        
                time.sleep(0.02)  # 20ms intervals
                
        def start_call(self, destination):
            try:
                # Set up audio callback
                self.client.set_audio_callback(self.audio_callback, 'pcm')
                
                # Connect
                print("Connecting...")
                self.client.connect()
                time.sleep(2)
                
                # Make call
                print(f"Calling {destination}...")
                self.client.make_call(destination)
                
                # Wait for connection
                while self.client.call_state.value not in ['connected', 'streaming']:
                    if self.client.call_state.value == 'idle':
                        print("Call failed")
                        return
                    time.sleep(0.1)
                    
                print(f"Call connected! Codec: {self.client.negotiated_codec}")
                
                # Set up audio streams
                self.audio = pyaudio.PyAudio()
                
                self.input_stream = self.audio.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK
                )
                
                self.output_stream = self.audio.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    output=True,
                    frames_per_buffer=self.CHUNK
                )
                
                # Start audio capture
                self.running = True
                audio_thread = threading.Thread(target=self.audio_capture_thread, daemon=True)
                audio_thread.start()
                
                print("Audio streaming active. Press Enter to hang up...")
                input()
                
            finally:
                self.cleanup()
                
        def cleanup(self):
            self.running = False
            
            if self.input_stream:
                self.input_stream.close()
            if self.output_stream:
                self.output_stream.close()
            if self.audio:
                self.audio.terminate()
                
            self.client.disconnect()
    
    # Usage
    if __name__ == "__main__":
        client = AudioCallClient("1001", "password", "192.168.1.100")  
        client.start_call("1002")

Call Status Monitoring
----------------------

Monitor call status and events:

.. code-block:: python

    from simplesip import SimpleSIPClient, CallState
    import time
    
    def monitor_call_status():
        client = SimpleSIPClient("1001", "password", "192.168.1.100")
        
        try:
            client.connect()
            time.sleep(2)
            
            client.make_call("1002")
            
            last_state = None
            
            while client.running:
                current_state = client.call_state
                
                # Log state changes
                if current_state != last_state:
                    status = client.get_call_status()
                    print(f"State changed: {current_state.value}")
                    print(f"  Call ID: {status['call_id']}")
                    print(f"  Remote RTP: {status['remote_rtp']}")
                    print(f"  Codec: {client.negotiated_codec}")
                    print(f"  Audio buffer: {status['audio_buffer_size']}")
                    print("-" * 40)
                    
                last_state = current_state
                
                if current_state == CallState.IDLE:
                    break
                    
                time.sleep(0.5)
                
        finally:
            client.disconnect()
    
    if __name__ == "__main__":
        monitor_call_status()

Multiple Calls Example
----------------------

Handle multiple simultaneous calls:

.. code-block:: python

    from simplesip import SimpleSIPClient
    import threading
    import time
    
    class MultiCallClient:
        def __init__(self):
            self.clients = {}
            
        def create_client(self, name, username, password, server):
            """Create a new SIP client"""
            client = SimpleSIPClient(username, password, server)
            self.clients[name] = client
            return client
            
        def make_call(self, client_name, destination):
            """Make a call using specified client"""
            if client_name in self.clients:
                client = self.clients[client_name]
                
                def call_thread():
                    try:
                        client.connect()
                        time.sleep(2)
                        client.make_call(destination)
                        
                        while client.call_state.value != 'idle':
                            time.sleep(1)
                            
                    except Exception as e:
                        print(f"Call error on {client_name}: {e}")
                        
                thread = threading.Thread(target=call_thread, daemon=True)
                thread.start()
                
        def disconnect_all(self):
            """Disconnect all clients"""
            for client in self.clients.values():
                try:
                    client.disconnect()
                except:
                    pass
    
    # Usage
    if __name__ == "__main__":
        multi_client = MultiCallClient()
        
        # Create multiple clients
        multi_client.create_client("alice", "1001", "pass1", "server.com")
        multi_client.create_client("bob", "1002", "pass2", "server.com") 
        
        # Make calls
        multi_client.make_call("alice", "9001")
        multi_client.make_call("bob", "9002")
        
        # Keep running
        try:
            time.sleep(60)  # Run for 1 minute
        finally:
            multi_client.disconnect_all()

DTMF Example
------------

Send DTMF tones during a call:

.. code-block:: python

    from simplesip import SimpleSIPClient
    import time
    
    def dtmf_example():
        client = SimpleSIPClient("1001", "password", "192.168.1.100")
        
        try:
            client.connect()
            time.sleep(2)
            
            client.make_call("1002")
            
            # Wait for connection
            while client.call_state.value != 'connected':
                time.sleep(0.1)
                
            print("Call connected! Sending DTMF tones...")
            
            # Send DTMF sequence
            dtmf_sequence = "1234*0#"
            
            for digit in dtmf_sequence:
                print(f"Sending DTMF: {digit}")
                client.send_dtmf(digit)
                time.sleep(0.5)  # Wait between tones
                
            print("DTMF sequence complete")
            input("Press Enter to hang up...")
            
        finally:
            client.disconnect()
    
    if __name__ == "__main__":
        dtmf_example()

These examples demonstrate the key features of SimpleSIP. Adapt them to your specific use case!