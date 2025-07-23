# SimpleSIP - Simple SIP Client Library

[![PyPI version](https://badge.fury.io/py/simplesip.svg)](https://badge.fury.io/py/simplesip)
[![Python Support](https://img.shields.io/pypi/pyversions/simplesip.svg)](https://pypi.org/project/simplesip/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight, easy-to-use Python library for SIP (Session Initiation Protocol) communication with RTP audio streaming capabilities. Perfect for building VoIP applications, automated calling systems, and SIP-based integrations.

## Features

- **Simple API** - Easy-to-use interface for SIP operations
- **Full SIP Support** - Registration, calls, and session management
- **Real-time Audio** - RTP audio streaming with μ-law (PCMU) encoding
- **Audio Capture** - Built-in microphone support with PyAudio integration
- **Authentication** - Digest authentication support
- **Async Operations** - Non-blocking operations with threading
- **Call States** - Comprehensive call state management
- **Extensible** - Easy to extend and customize for your needs

## Quick Start

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
client.call("1234567890")

# Wait for the call to be established
while client.call_state.value != 'connected':
    time.sleep(0.1)

# Keep the call active for 10 seconds
time.sleep(10)

# Hang up
client.hangup()

# Disconnect from server
client.disconnect()
```

## API Reference

### SimpleSIPClient

The main class for SIP operations.

#### Constructor

```python
SimpleSIPClient(username, password, server, port=5060, local_port=None, timeout=5)
```

**Parameters:**
- `username` (str): SIP username
- `password` (str): SIP password
- `server` (str): SIP server hostname or IP
- `port` (int): SIP server port (default: 5060)
- `local_port` (int): Local port for SIP (default: random)
- `timeout` (int): Connection timeout in seconds (default: 5)

#### Methods

##### connect()
Connect to the SIP server and register.

```python
client.connect()
```

##### call(number)
Initiate a call to the specified number.

```python
client.call("1234567890")
```

##### hangup()
End the current call.

```python
client.hangup()
```

##### disconnect()
Disconnect from the SIP server.

```python
client.disconnect()
```

##### send_audio(audio_data)
Send audio data during an active call.

```python
client.send_audio(ulaw_audio_data)
```

##### set_audio_callback(callback, format='pcmu')
Set a callback function to handle incoming audio.

```python
def audio_handler(audio_data, format):
    # Process incoming audio
    pass

client.set_audio_callback(audio_handler, format='pcmu')
```

##### get_call_status()
Get the current call status.

```python
status = client.get_call_status()
print(f"State: {status['state']}")
print(f"Duration: {status['duration']}")
```

### Call States

The library uses an enum for call states:

- `CallState.IDLE` - No active call
- `CallState.INVITING` - Outgoing call in progress
- `CallState.RINGING` - Call is ringing
- `CallState.CONNECTED` - Call connected but no media
- `CallState.STREAMING` - Call with active audio streaming

## Audio Support

SimpleSIP supports real-time audio streaming using RTP protocol with μ-law (PCMU) encoding.

### Audio Formats

- **PCMU (μ-law)**: Primary format for SIP/RTP
- **PCM**: Linear 16-bit audio for processing

### Audio Callback

Set up an audio callback to handle incoming audio:

```python
def handle_audio(audio_data, format):
    if format == 'pcmu':
        # Handle μ-law encoded audio
        pass
    elif format == 'pcm':
        # Handle linear PCM audio
        pass

client.set_audio_callback(handle_audio, format='pcmu')
```

### Microphone Integration

```python
import pyaudio
import numpy as np

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

# Capture and send audio
while client.call_state.value in ['connected', 'streaming']:
    data = stream.read(CHUNK)
    # Convert PCM to μ-law (implement conversion)
    ulaw_data = pcm_to_ulaw(data)
    client.send_audio(ulaw_data)
```

## Examples

### Complete Call Example

```python
from simplesip import SimpleSIPClient
import time
import threading

def audio_callback(audio_data, format):
    """Handle incoming audio data"""
    print(f"Received {len(audio_data)} bytes of {format} audio")

# Create client
client = SimpleSIPClient(
    username="1001",
    password="secret123",
    server="sip.example.com"
)

# Set up audio handling
client.set_audio_callback(audio_callback, format='pcmu')

try:
    # Connect to server
    print("Connecting to SIP server...")
    client.connect()
    print("Connected and registered!")
    
    # Make a call
    print("Making call to 1002...")
    client.call("1002")
    
    # Wait for call to be answered
    timeout = 30
    start_time = time.time()
    
    while client.call_state.value not in ['connected', 'streaming']:
        if time.time() - start_time > timeout:
            print("Call timeout!")
            break
        
        status = client.get_call_status()
        print(f"Call status: {status['state']}")
        time.sleep(1)
    
    if client.call_state.value in ['connected', 'streaming']:
        print("Call connected! Audio streaming active.")
        
        # Keep call active for 30 seconds
        time.sleep(30)
        
        # Hang up
        print("Hanging up...")
        client.hangup()
    
finally:
    # Clean disconnect
    client.disconnect()
    print("Disconnected from server")
```

### Configuration Options

```python
# Create client with custom settings
client = SimpleSIPClient(
    username="myuser",
    password="mypass",
    server="192.168.1.100",
    port=5060,           # Custom SIP port
    local_port=5061,     # Custom local port
    timeout=10           # Custom timeout
)

# Set custom timeout
client.timeout = 30

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Requirements

- Python 3.8+
- numpy (for audio processing)
- pyaudio (optional, for microphone support)

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=simplesip
```

### Building Documentation

```bash
# Install docs dependencies
pip install sphinx sphinx-rtd-theme

# Build docs
cd docs
make html
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pytest`
6. Commit changes: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature-name`
8. Submit a Pull Request

## Known Limitations

- Currently supports PCMU (μ-law) audio encoding only
- IPv4 only (IPv6 support planned)
- Basic SIP features (advanced features in development)
- No built-in STUN/TURN support yet

## Roadmap

- [ ] Additional audio codecs (G.711 A-law, G.722)
- [ ] IPv6 support
- [ ] STUN/TURN support for NAT traversal
- [ ] SIP over TLS (SIPS)
- [ ] Conference calling support
- [ ] Call transfer and hold functionality
- [ ] Advanced SDP negotiation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Awais Khan**
- Email: [contact@awaiskhan.com.pk](mailto:contact@awaiskhan.com.pk)
- GitHub: [@Awaiskhan404](https://github.com/Awaiskhan404)

## Acknowledgments

- Built with Python's socket and threading libraries
- Audio processing powered by NumPy
- Inspired by the SIP protocol specification (RFC 3261)

## Support

- **Bug Reports**: [GitHub Issues](https://github.com/Awaiskhan404/simplesip/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Awaiskhan404/simplesip/discussions)
- **Email**: [contact@awaiskhan.com.pk](mailto:contact@awaiskhan.com.pk)

---

*Made with ❤️ for the Python and VoIP communities*