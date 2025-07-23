# SimpleSIP - Simple SIP Client Library

[![PyPI version](https://badge.fury.io/py/simplesip.svg)](https://badge.fury.io/py/simplesip)
[![Python Support](https://img.shields.io/pypi/pyversions/simplesip.svg)](https://pypi.org/project/simplesip/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight, easy-to-use Python library for SIP (Session Initiation Protocol) communication with RTP audio streaming capabilities. Perfect for building VoIP applications, automated calling systems, and SIP-based integrations.

## ( Features

- =€ **Simple API** - Easy-to-use interface for SIP operations
- =Þ **Full SIP Support** - Registration, calls, and session management
- <µ **Real-time Audio** - RTP audio streaming with ¼-law (PCMU) encoding
- <¤ **Audio Capture** - Built-in microphone support with PyAudio integration
- = **Authentication** - Digest authentication support
- >õ **Async Operations** - Non-blocking operations with threading
- =Ê **Call States** - Comprehensive call state management
- =à **Extensible** - Easy to extend and customize for your needs

## =€ Quick Start

### Installation

```bash
pip install simplesip
```

For audio support, install with optional dependencies:
```bash
pip install simplesip[audio]
# or
pip install simplesip pyaudio
```

### Basic Usage

```python
from simplesip import SimpleSIPClient
import time

# Create a SIP client
client = SimpleSIPClient(
    username="your_username",
    password="your_password", 
    server="your_sip_server.com"
)

# Connect to the SIP server
client.connect()

# Make a call
client.make_call("1001")  # Call extension 1001

# Wait for call to establish
time.sleep(5)

# End the call
client.disconnect()
```

### Advanced Usage with Audio

```python
from simplesip import SimpleSIPClient
import time

def audio_received_callback(audio_data, format='pcmu'):
    """Handle incoming audio data"""
    print(f"Received {len(audio_data)} bytes of {format} audio")
    # Process audio data here

# Create client with audio callback
client = SimpleSIPClient("username", "password", "server.com")
client.set_audio_callback(audio_received_callback)

# Connect and make call
client.connect()
client.make_call("1002")

# Keep call active
while client.call_state.value != 'idle':
    status = client.get_call_status()
    print(f"Call status: {status['state']}")
    time.sleep(1)

client.disconnect()
```

## =Ú API Reference

### SimpleSIPClient

The main class for SIP operations.

#### Constructor

```python
SimpleSIPClient(username: str, password: str, server: str, port: int = 5060)
```

**Parameters:**
- `username` (str): SIP username/extension
- `password` (str): SIP password
- `server` (str): SIP server IP address or hostname
- `port` (int): SIP server port (default: 5060)

#### Methods

##### Connection Management

```python
client.connect() -> bool
```
Connect to the SIP server and register.

```python
client.disconnect()
```
Disconnect from SIP server and cleanup.

##### Call Operations

```python
client.make_call(destination: str) -> bool
```
Initiate a call to the specified destination.

```python
client.answer_call() -> bool
```
Answer an incoming call.

```python
client.end_call()
```
End the current active call.

##### Audio Operations

```python
client.set_audio_callback(callback_func: callable, format: str = 'pcmu')
```
Set callback function for incoming audio data.

```python
client.send_audio(audio_data: bytes)
```
Send audio data via RTP.

##### Status and Information

```python
client.get_call_status() -> dict
```
Get current call status and information.

```python
client.call_state -> CallState
```
Current call state (IDLE, INVITING, RINGING, CONNECTED, STREAMING).

### Call States

The library uses an enum for call states:

- `CallState.IDLE` - No active call
- `CallState.INVITING` - Outgoing call in progress
- `CallState.RINGING` - Call is ringing
- `CallState.CONNECTED` - Call connected but no media
- `CallState.STREAMING` - Call with active audio streaming

## <µ Audio Support

SimpleSIP supports real-time audio streaming using RTP protocol with ¼-law (PCMU) encoding.

### Audio Formats

- **PCMU (¼-law)**: Primary format for SIP/RTP
- **PCM**: Linear 16-bit audio for processing

### Audio Callback

Set up an audio callback to handle incoming audio:

```python
def handle_audio(audio_data, format):
    if format == 'pcmu':
        # Handle ¼-law encoded audio
        pass
    elif format == 'pcm':
        # Handle linear PCM audio
        pass

client.set_audio_callback(handle_audio, format='pcmu')
```

### Microphone Integration

Example with PyAudio for microphone input:

```python
import pyaudio
import numpy as np

# Audio configuration
CHUNK = 160  # 20ms at 8kHz
RATE = 8000
FORMAT = pyaudio.paInt16

audio = pyaudio.PyAudio()
stream = audio.open(
    format=FORMAT,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

# Capture and send audio
while client.call_state.value in ['connected', 'streaming']:
    data = stream.read(CHUNK)
    # Convert PCM to ¼-law (implement conversion)
    ulaw_data = pcm_to_ulaw(data)
    client.send_audio(ulaw_data)
```

## =Ö Examples

### Complete Call Example

```python
from simplesip import SimpleSIPClient
import time
import threading

class VoIPApp:
    def __init__(self):
        self.client = SimpleSIPClient("1001", "password", "192.168.1.100")
        self.client.set_audio_callback(self.on_audio_received)
        
    def on_audio_received(self, audio_data, format):
        # Play or process received audio
        print(f"Received audio: {len(audio_data)} bytes")
        
    def make_call(self, number):
        if self.client.connect():
            print("Connected to SIP server")
            
            if self.client.make_call(number):
                print(f"Calling {number}...")
                
                # Wait for call to connect
                while self.client.call_state.value not in ['connected', 'streaming']:
                    if self.client.call_state.value == 'idle':
                        print("Call failed or ended")
                        return
                    time.sleep(0.1)
                
                print("Call connected!")
                
                # Keep call active for 30 seconds
                time.sleep(30)
                
                self.client.end_call()
                print("Call ended")
            
            self.client.disconnect()

# Usage
app = VoIPApp()
app.make_call("1002")
```

### Server Integration Example

```python
from simplesip import SimpleSIPClient
import asyncio

class SIPServer:
    def __init__(self):
        self.clients = {}
    
    async def handle_incoming_call(self, client_id, caller_number):
        client = SimpleSIPClient("extension", "password", "server")
        client.set_audio_callback(lambda data, fmt: self.relay_audio(data, client_id))
        
        if client.connect():
            await asyncio.sleep(1)  # Ring simulation
            client.answer_call()
            
            # Handle call...
            await asyncio.sleep(10)
            
            client.end_call()
            client.disconnect()
    
    def relay_audio(self, audio_data, client_id):
        # Relay audio to other clients or process
        pass
```

## =' Configuration

### Environment Variables

Set default configuration using environment variables:

```bash
export SIMPLESIP_SERVER="your-sip-server.com"
export SIMPLESIP_USERNAME="your-username"
export SIMPLESIP_PASSWORD="your-password"
```

### Advanced Configuration

```python
client = SimpleSIPClient("user", "pass", "server")

# Configure RTP port range
client.local_rtp_port = 10000

# Set custom timeout
client.timeout = 30

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## =à Development

### Requirements

- Python 3.8+
- numpy (for audio processing)
- pyaudio (optional, for microphone support)

### Running Tests

```bash
pip install -e .[dev]
pytest
```

### Code Quality

```bash
# Format code
black simplesip/

# Type checking
mypy simplesip/

# Linting
flake8 simplesip/
```

## > Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pytest`
6. Commit changes: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature-name`
8. Submit a Pull Request

##   Known Limitations

- Currently supports PCMU (¼-law) audio encoding only
- IPv4 only (IPv6 support planned)
- Basic SIP features (advanced features in development)
- No built-in STUN/TURN support yet

## =ú Roadmap

- [ ] Additional audio codecs (G.711 A-law, G.722)
- [ ] IPv6 support
- [ ] STUN/TURN support for NAT traversal
- [ ] SIP over TLS (SIPS)
- [ ] Conference calling support
- [ ] Call transfer and hold functionality
- [ ] Advanced SDP negotiation

## =Ä License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## =h=» Author

**Awais Khan**
- Email: [contact@awaiskhan.com.pk](mailto:contact@awaiskhan.com.pk)
- GitHub: [@Awaiskhan404](https://github.com/Awaiskhan404)

## =O Acknowledgments

- Built with Python's socket and threading libraries
- Audio processing powered by NumPy
- Inspired by the SIP protocol specification (RFC 3261)

## =Þ Support

- = **Bug Reports**: [GitHub Issues](https://github.com/Awaiskhan404/simplesip/issues)
- =¬ **Discussions**: [GitHub Discussions](https://github.com/Awaiskhan404/simplesip/discussions)
- =ç **Email**: [contact@awaiskhan.com.pk](mailto:contact@awaiskhan.com.pk)

---

*Made with d for the Python and VoIP communities*