# SimpleSIP API Documentation

## Table of Contents

- [SimpleSIPClient](#simplesiplient)
- [CallState Enum](#callstate-enum)
- [Audio Handling](#audio-handling)
- [Error Handling](#error-handling)
- [Examples](#examples)

## SimpleSIPClient

The main class for SIP communication operations.

### Constructor

```python
SimpleSIPClient(username: str, password: str, server: str, port: int = 5060)
```

Creates a new SimpleSIP client instance.

**Parameters:**
- `username` (str): SIP username or extension number
- `password` (str): SIP account password  
- `server` (str): SIP server IP address or hostname
- `port` (int, optional): SIP server port. Defaults to 5060.

**Example:**
```python
client = SimpleSIPClient("1001", "mypassword", "192.168.1.100")
```

### Properties

#### call_state
```python
@property
call_state -> CallState
```
Current state of the call connection.

**Returns:** CallState enum value

**Example:**
```python
if client.call_state == CallState.CONNECTED:
    print("Call is active")
```

#### running
```python
@property  
running -> bool
```
Whether the SIP client is currently running and connected.

**Returns:** True if client is active, False otherwise

### Connection Management

#### connect()
```python
connect() -> bool
```
Connect to the SIP server and register the client.

**Returns:** True if connection successful, False otherwise

**Raises:**
- `ConnectionError`: If unable to connect to server
- `AuthenticationError`: If credentials are invalid

**Example:**
```python
if client.connect():
    print("Successfully connected to SIP server") 
else:
    print("Failed to connect")
```

#### disconnect()
```python
disconnect() -> None
```
Disconnect from SIP server and cleanup all resources.

**Example:**
```python
client.disconnect()
print("Disconnected from server")
```

### Call Operations

#### make_call()
```python
make_call(destination: str) -> bool
```
Initiate an outbound call to the specified destination.

**Parameters:**
- `destination` (str): Phone number, extension, or SIP URI to call

**Returns:** True if call initiation successful, False otherwise

**Raises:**
- `ConnectionError`: If not connected to SIP server
- `ValueError`: If destination format is invalid

**Example:**
```python
success = client.make_call("1002")
if success:
    print("Call initiated successfully")
```

#### answer_call()
```python
answer_call() -> bool
```
Answer an incoming call.

**Returns:** True if call answered successfully, False otherwise

**Raises:**
- `RuntimeError`: If no incoming call to answer

**Example:**
```python
# In incoming call handler
if client.answer_call():
    print("Call answered")
```

#### end_call()
```python
end_call() -> None
```
Terminate the current active call.

**Example:**
```python
client.end_call()
print("Call ended")
```

### Audio Operations

#### set_audio_callback()
```python
set_audio_callback(callback: Callable[[bytes, str], None], format: str = 'pcmu') -> None
```
Set callback function to handle incoming audio data.

**Parameters:**
- `callback`: Function to call when audio data received
  - `audio_data` (bytes): Raw audio data
  - `format` (str): Audio format ('pcmu' or 'pcm')
- `format` (str, optional): Preferred audio format. Defaults to 'pcmu'.

**Example:**
```python
def handle_audio(audio_data, format):
    print(f"Received {len(audio_data)} bytes of {format} audio")
    # Process audio here

client.set_audio_callback(handle_audio, format='pcmu')
```

#### send_audio()
```python
send_audio(audio_data: bytes) -> None
```
Send audio data via RTP to the remote party.

**Parameters:**
- `audio_data` (bytes): Audio data in μ-law (PCMU) format

**Raises:**
- `RuntimeError`: If no active call or RTP session

**Example:**
```python
# Send μ-law encoded audio
client.send_audio(ulaw_audio_bytes)
```

### Status and Information

#### get_call_status()
```python
get_call_status() -> Dict[str, Any]
```
Get comprehensive information about the current call state.

**Returns:** Dictionary containing call status information:
- `state` (str): Current call state name
- `remote_rtp` (Optional[Tuple[str, int]]): Remote RTP endpoint  
- `local_rtp_port` (int): Local RTP port number
- `audio_buffer_size` (int): Current audio buffer size
- `call_duration` (float): Duration of current call in seconds

**Example:**
```python
status = client.get_call_status()
print(f"Call state: {status['state']}")
print(f"Duration: {status['call_duration']:.1f}s")
```

## CallState Enum

Enumeration of possible call states.

```python
from enum import Enum

class CallState(Enum):
    IDLE = "idle"
    INVITING = "inviting"
    RINGING = "ringing" 
    CONNECTED = "connected"
    STREAMING = "streaming"
```

### States Description

- **IDLE**: No active call, client ready for new operations
- **INVITING**: Outgoing call initiated, waiting for response
- **RINGING**: Call is ringing on remote end
- **CONNECTED**: Call established but no media flow yet
- **STREAMING**: Active call with audio streaming

### Usage Example

```python
from simplesip import SimpleSIPClient, CallState

client = SimpleSIPClient("user", "pass", "server")
client.connect()
client.make_call("1001")

# Wait for call to connect
while client.call_state != CallState.CONNECTED:
    if client.call_state == CallState.IDLE:
        print("Call failed")
        break
    time.sleep(0.1)

if client.call_state == CallState.CONNECTED:
    print("Call successful!")
```

## Audio Handling

### Audio Formats

SimpleSIP supports these audio formats:

#### PCMU (μ-law)
- **Description**: ITU-T G.711 μ-law compression
- **Sample Rate**: 8 kHz
- **Bit Depth**: 8-bit compressed
- **Usage**: Primary format for SIP/RTP transmission

#### PCM (Linear)
- **Description**: Uncompressed linear audio
- **Sample Rate**: 8 kHz  
- **Bit Depth**: 16-bit signed
- **Usage**: Audio processing and conversion

### Audio Callback Function

The audio callback function receives incoming RTP audio data:

```python
def audio_callback(audio_data: bytes, format: str) -> None:
    """
    Handle incoming audio data.
    
    Args:
        audio_data: Raw audio bytes
        format: Audio format ('pcmu' or 'pcm')
    """
    if format == 'pcmu':
        # Process μ-law audio
        decoded_audio = ulaw_to_pcm(audio_data)
        play_audio(decoded_audio)
    elif format == 'pcm':
        # Process linear PCM audio
        play_audio(audio_data)
```

### Audio Conversion

#### μ-law to PCM Conversion

```python
import numpy as np

def ulaw_to_pcm(ulaw_data: bytes) -> bytes:
    """Convert μ-law audio to 16-bit PCM."""
    ulaw_samples = np.frombuffer(ulaw_data, dtype=np.uint8)
    
    # μ-law decompression
    ulaw_samples = ulaw_samples ^ 0xFF  # Complement bits
    sign = (ulaw_samples & 0x80) >> 7
    exponent = (ulaw_samples & 0x70) >> 4
    mantissa = ulaw_samples & 0x0F
    
    # Calculate linear value
    linear = ((mantissa << 3) + 0x84) << exponent
    linear = np.where(sign == 1, -linear, linear)
    
    return linear.astype(np.int16).tobytes()
```

#### PCM to μ-law Conversion

```python
def pcm_to_ulaw(pcm_data: bytes) -> bytes:
    """Convert 16-bit PCM to μ-law audio."""
    pcm_samples = np.frombuffer(pcm_data, dtype=np.int16)
    
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
        
        # Find exponent
        exp = 7
        while exp > 0 and sample < (0x1 << (exp + 7)):
            exp -= 1
        
        # Calculate mantissa
        mantissa = (sample >> (exp + 3)) & 0x0F
        
        # Combine and complement
        ulaw_byte = sign | (exp << 4) | mantissa
        ulaw_samples.append(ulaw_byte ^ 0xFF)
    
    return bytes(ulaw_samples)
```

## Error Handling

### Exception Types

SimpleSIP raises these custom exceptions:

#### ConnectionError
Raised when SIP server connection fails.

```python
try:
    client.connect()
except ConnectionError as e:
    print(f"Connection failed: {e}")
```

#### AuthenticationError
Raised when SIP authentication fails.

```python
try:
    client.connect()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

#### CallError
Raised when call operations fail.

```python
try:
    client.make_call("invalid_number")
except CallError as e:
    print(f"Call failed: {e}")
```

### Error Handling Best Practices

```python
import logging
from simplesip import SimpleSIPClient, ConnectionError, CallError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_reliable_call(username, password, server, destination):
    client = SimpleSIPClient(username, password, server)
    
    try:
        # Connect with retry logic
        if not client.connect():
            raise ConnectionError("Failed to connect after retries")
        
        logger.info("Connected to SIP server")
        
        # Make call with timeout
        if client.make_call(destination):
            logger.info(f"Calling {destination}")
            
            # Wait for call with timeout
            timeout = 30
            start_time = time.time()
            
            while client.call_state.value not in ['connected', 'streaming']:
                if time.time() - start_time > timeout:
                    raise CallError("Call timeout")
                    
                if client.call_state.value == 'idle':
                    raise CallError("Call failed or rejected")
                    
                time.sleep(0.1)
            
            logger.info("Call connected successfully")
            return client
            
        else:
            raise CallError("Failed to initiate call")
            
    except (ConnectionError, CallError) as e:
        logger.error(f"Call operation failed: {e}")
        if client:
            client.disconnect()
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if client:
            client.disconnect()
        raise
```

## Examples

### Basic Call Example

```python
from simplesip import SimpleSIPClient
import time

# Create and configure client
client = SimpleSIPClient("1001", "password", "192.168.1.100")

try:
    # Connect to server
    if client.connect():
        print("Connected to SIP server")
        
        # Make outbound call
        if client.make_call("1002"):
            print("Call initiated to 1002")
            
            # Wait for call to connect
            while client.call_state.value not in ['connected', 'streaming']:
                print(f"Call state: {client.call_state.value}")
                time.sleep(1)
            
            print("Call connected!")
            
            # Keep call active for 30 seconds
            time.sleep(30)
            
        # End call
        client.end_call()
        print("Call ended")
        
finally:
    # Always disconnect
    client.disconnect()
```

### Audio Streaming Example

```python
from simplesip import SimpleSIPClient
import pyaudio
import threading
import time

class AudioCallHandler:
    def __init__(self):
        self.client = None
        self.audio = None
        self.stream = None
        self.running = False
        
    def audio_callback(self, audio_data, format):
        """Handle incoming audio"""
        if format == 'pcmu' and self.stream:
            # Convert μ-law to PCM and play
            pcm_data = self.ulaw_to_pcm(audio_data)
            if self.stream and not self.stream._stopped:
                try:
                    self.stream.write(pcm_data)
                except:
                    pass  # Handle audio playback errors
    
    def setup_audio(self):
        """Initialize audio system"""
        self.audio = pyaudio.PyAudio()
        
        # Output stream for playback
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=8000,
            output=True,
            frames_per_buffer=160
        )
    
    def cleanup_audio(self):
        """Cleanup audio resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
    
    def make_call_with_audio(self, username, password, server, destination):
        """Make call with audio streaming"""
        self.client = SimpleSIPClient(username, password, server)
        self.client.set_audio_callback(self.audio_callback)
        
        try:
            # Setup audio
            self.setup_audio()
            
            # Connect and call
            if self.client.connect():
                print("Connected to SIP server")
                
                if self.client.make_call(destination):
                    print(f"Calling {destination}...")
                    
                    # Wait for connection
                    while self.client.call_state.value not in ['connected', 'streaming']:
                        if self.client.call_state.value == 'idle':
                            print("Call failed")
                            return
                        time.sleep(0.1)
                    
                    print("Call connected with audio!")
                    self.running = True
                    
                    # Keep call active
                    while self.running and self.client.call_state.value != 'idle':
                        time.sleep(1)
                    
                    print("Call ended")
                
        except KeyboardInterrupt:
            print("Call interrupted by user")
            
        finally:
            if self.client:
                self.client.end_call()
                self.client.disconnect()
            self.cleanup_audio()
    
    def ulaw_to_pcm(self, ulaw_data):
        """Convert μ-law to PCM (simplified)"""
        # Implementation here
        pass

# Usage
handler = AudioCallHandler()
handler.make_call_with_audio("1001", "password", "server.com", "1002")
```

### Server Integration Example

```python
from simplesip import SimpleSIPClient
import asyncio
import threading
from typing import Dict, Optional

class SIPCallManager:
    def __init__(self):
        self.active_calls: Dict[str, SimpleSIPClient] = {}
        self.call_handlers = {}
    
    async def handle_incoming_call(self, call_id: str, from_number: str):
        """Handle incoming call"""
        print(f"Incoming call {call_id} from {from_number}")
        
        # Create client for this call
        client = SimpleSIPClient("auto_answer", "password", "server")
        client.set_audio_callback(
            lambda data, fmt: self.relay_audio(call_id, data, fmt)
        )
        
        try:
            if client.connect():
                # Answer the call
                if client.answer_call():
                    print(f"Answered call {call_id}")
                    self.active_calls[call_id] = client
                    
                    # Monitor call state
                    while client.call_state.value != 'idle':
                        await asyncio.sleep(1)
                    
                    print(f"Call {call_id} ended")
                
        except Exception as e:
            print(f"Error handling call {call_id}: {e}")
            
        finally:
            if call_id in self.active_calls:
                del self.active_calls[call_id]
            client.disconnect()
    
    def relay_audio(self, call_id: str, audio_data: bytes, format: str):
        """Relay audio between calls or to external systems"""
        # Implement audio relay logic
        print(f"Relaying {len(audio_data)} bytes from call {call_id}")
    
    def make_outbound_call(self, call_id: str, destination: str) -> bool:
        """Make outbound call"""
        client = SimpleSIPClient("outbound", "password", "server")
        
        if client.connect():
            if client.make_call(destination):
                self.active_calls[call_id] = client
                return True
        
        return False
    
    def end_call(self, call_id: str):
        """End specific call"""
        if call_id in self.active_calls:
            client = self.active_calls[call_id]
            client.end_call()
            client.disconnect()
            del self.active_calls[call_id]
    
    def shutdown(self):
        """Shutdown all calls"""
        for call_id in list(self.active_calls.keys()):
            self.end_call(call_id)

# Usage
manager = SIPCallManager()

# Handle incoming call
asyncio.run(manager.handle_incoming_call("call_1", "1001"))

# Make outbound call  
success = manager.make_outbound_call("call_2", "1002")

# Cleanup
manager.shutdown()
```