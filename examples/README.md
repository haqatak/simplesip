# SimpleSIP Examples

This directory contains example scripts demonstrating various features of SimpleSIP.

## Examples Overview

### 1. Simple Call (`simple_call.py`)
Basic example showing how to make a SIP call without audio.

**Features:**
- Connect to SIP server
- Make outbound call
- Monitor call state
- Handle call completion

**Usage:**
```bash
python simple_call.py
```

**Configuration:**
Edit the script to update:
- `USERNAME` - Your SIP username
- `PASSWORD` - Your SIP password
- `SERVER` - Your SIP server IP
- `DESTINATION` - Number to call

### 2. Audio Call (`audio_call.py`)
Advanced example with full audio streaming support.

**Features:**
- Real-time audio streaming
- Microphone input capture
- Speaker output playback
- μ-law audio conversion
- Multi-threaded audio processing

**Requirements:**
```bash
pip install pyaudio numpy
```

**Usage:**
```bash
python audio_call.py [destination_number]
```

**Configuration:**
Edit the script to update your SIP credentials and server details.

## Running the Examples

### Prerequisites

1. **Python 3.8+** installed
2. **SimpleSIP** installed:
   ```bash
   pip install simplesip
   ```

3. **Audio support** (for audio_call.py):
   ```bash
   pip install simplesip[audio]
   # or
   pip install pyaudio numpy
   ```

4. **SIP Server Access**:
   - SIP server IP address
   - Valid SIP credentials (username/password)
   - Network connectivity to SIP server

### Configuration Steps

1. **Edit Example Scripts:**
   Update the configuration section in each script:
   ```python
   USERNAME = "your_username"    # Your SIP extension
   PASSWORD = "your_password"    # Your SIP password
   SERVER = "192.168.1.100"      # Your SIP server IP
   DESTINATION = "1002"          # Number to call
   ```

2. **Network Setup:**
   - Ensure firewall allows SIP (port 5060) and RTP traffic
   - Configure NAT/router if needed
   - Test network connectivity to SIP server

3. **Audio Setup** (for audio examples):
   - Connect microphone and speakers
   - Test audio devices work with your system
   - Adjust audio levels as needed

### Example Output

#### Simple Call Example
```
SimpleSIP - Simple Call Example
========================================
Connecting to SIP server 192.168.1.100...
✅ Connected to SIP server
📞 Calling 1002...
📤 Call initiated, waiting for response...
📋 Call state: inviting
📋 Call state: ringing
✅ Call connected successfully!
🔊 Call is active...
⏱️  Keeping call active for 10 seconds
📊 Status: connected | Duration: 1s
📊 Status: streaming | Duration: 2s
...
🔚 Ending call...
✅ Call ended successfully
🔌 Disconnecting from server...
👋 Goodbye!
```

#### Audio Call Example
```
SimpleSIP - Audio Call Example
========================================
🎤 Audio initialized - 8000Hz, 1 channel(s)
📡 Connecting to SIP server...
✅ Connected to SIP server
📞 Calling 1002...
📤 Call initiated, waiting for response...
📋 Call state: inviting
📋 Call state: ringing
✅ Call connected with audio streaming!
🎤 Speak into your microphone
🔊 Audio will be played through speakers
Press Ctrl+C to end the call
🎵 Audio streaming started
📊 Status: streaming | RTP: ('192.168.1.102', 5004) | Buffer: 0
```

## Troubleshooting

### Common Issues

#### Connection Problems
```
❌ Failed to connect to SIP server
```
**Solutions:**
- Check SIP server IP address and port
- Verify network connectivity
- Check firewall settings
- Confirm SIP server is running

#### Authentication Failures
```
❌ Failed to connect to SIP server
```
**Solutions:**
- Verify username and password
- Check SIP account is active
- Confirm account permissions

#### Audio Issues
```
❌ Failed to initialize audio: [Errno -9996] Invalid input device
```
**Solutions:**
- Check microphone is connected
- Verify PyAudio installation
- Test with different audio devices
- Check system audio settings

#### Call Failures
```
❌ Call failed or was rejected
```
**Solutions:**
- Verify destination number exists
- Check destination is online/available
- Confirm calling permissions
- Try different destination

### Debug Mode

Enable debug logging for more detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Add this to the beginning of any example script.

### Testing Network Connectivity

Test basic connectivity to your SIP server:

```bash
# Test TCP connectivity
telnet your_sip_server 5060

# Test UDP (if supported by your system)
nc -u your_sip_server 5060
```

## Creating Custom Examples

### Basic Template

```python
from simplesip import SimpleSIPClient
import time

def my_sip_example():
    # Configuration
    client = SimpleSIPClient("username", "password", "server")
    
    try:
        # Connect
        if client.connect():
            print("Connected!")
            
            # Your SIP operations here
            # ...
            
        else:
            print("Connection failed")
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        client.disconnect()

if __name__ == "__main__":
    my_sip_example()
```

### Audio Template

```python
from simplesip import SimpleSIPClient
import pyaudio

class MyAudioHandler:
    def __init__(self):
        self.client = SimpleSIPClient("user", "pass", "server")
        self.client.set_audio_callback(self.on_audio_received)
        
    def on_audio_received(self, audio_data, format):
        # Handle incoming audio
        print(f"Received {len(audio_data)} bytes of {format} audio")
        
    def setup_audio(self):
        # Initialize PyAudio
        pass
        
    def run(self):
        self.setup_audio()
        
        if self.client.connect():
            # Your audio call logic
            pass
            
        self.client.disconnect()

# Usage
handler = MyAudioHandler()
handler.run()
```

## Contributing Examples

We welcome contributions of new examples! Please:

1. Follow the existing code style
2. Include comprehensive comments
3. Add configuration instructions
4. Test thoroughly
5. Update this README

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

## Support

For questions about these examples:
- 📖 Check the main [README.md](../README.md)
- 🐛 Report issues on [GitHub](https://github.com/Awaiskhan404/simplesip/issues)
- 💬 Start a [discussion](https://github.com/Awaiskhan404/simplesip/discussions)
- 📧 Email: [contact@awaiskhan.com.pk](mailto:contact@awaiskhan.com.pk)