Audio Codecs
============

SimpleSIP supports multiple audio codecs for different quality and bandwidth requirements.

Supported Codecs
----------------

G.722 (High Quality)
~~~~~~~~~~~~~~~~~~~~

* **Sample Rate**: 16 kHz (internally), 8 kHz RTP clock
* **Bit Rate**: 64 kbps  
* **Quality**: High definition audio
* **RTP Payload Type**: 9
* **Use Case**: Best quality, modern SIP servers

.. code-block:: python

    # G.722 is automatically preferred when available
    client = SimpleSIPClient("user", "pass", "server.com")
    client.connect()
    client.make_call("1234")
    
    # Check if G.722 was negotiated
    if client.negotiated_codec == "G722":
        print("Using high-quality G.722 codec!")

PCMU (G.711 μ-law)
~~~~~~~~~~~~~~~~~~

* **Sample Rate**: 8 kHz
* **Bit Rate**: 64 kbps
* **Quality**: Standard telephony quality
* **RTP Payload Type**: 0  
* **Use Case**: Default codec, universal compatibility

.. code-block:: python

    # PCMU is the fallback codec
    # Most compatible with legacy systems

PCMA (G.711 A-law) 
~~~~~~~~~~~~~~~~~~

* **Sample Rate**: 8 kHz
* **Bit Rate**: 64 kbps
* **Quality**: Standard telephony quality
* **RTP Payload Type**: 8
* **Use Case**: European/international systems

Codec Negotiation
-----------------

SimpleSIP automatically negotiates the best available codec:

1. **G.722** - Preferred for high quality
2. **PCMU** - Fallback for compatibility  
3. **PCMA** - Alternative fallback

.. code-block:: python

    client = SimpleSIPClient("user", "pass", "server.com")
    client.connect()
    client.make_call("1234")
    
    # Wait for negotiation
    while not client.negotiated_codec:
        time.sleep(0.1)
        
    print(f"Negotiated codec: {client.negotiated_codec}")
    print(f"Payload type: {client.negotiated_payload_type}")

Audio Quality Comparison
------------------------

+----------+-------------+----------+---------------+
| Codec    | Sample Rate | Bit Rate | Quality       |
+==========+=============+==========+===============+
| G.722    | 16 kHz      | 64 kbps  | HD Audio      |
+----------+-------------+----------+---------------+
| PCMU     | 8 kHz       | 64 kbps  | Standard      |
+----------+-------------+----------+---------------+
| PCMA     | 8 kHz       | 64 kbps  | Standard      |
+----------+-------------+----------+---------------+

Configuring Server for G.722
-----------------------------

To enable G.722 on your SIP server:

Asterisk Configuration
~~~~~~~~~~~~~~~~~~~~~~

Add to ``/etc/asterisk/sip.conf`` or ``/etc/asterisk/pjsip.conf``:

.. code-block:: ini

    [general]
    disallow=all
    allow=g722
    allow=ulaw
    allow=alaw
    
    [1001]  ; Your extension
    type=friend
    secret=password
    host=dynamic
    context=default
    disallow=all
    allow=g722
    allow=ulaw

FreeSWITCH Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

Add to your dialplan or user configuration:

.. code-block:: xml

    <action application="set" data="codec_string=G722,PCMU,PCMA"/>

Testing Codec Quality
----------------------

Use this script to test different codecs:

.. code-block:: python

    from simplesip import SimpleSIPClient
    import time
    
    def test_codec_quality():
        client = SimpleSIPClient("1001", "password", "server.com")
        
        try:
            client.connect()
            time.sleep(2)
            
            print("Making test call...")
            client.make_call("1002")
            
            # Wait for connection
            while client.call_state.value != 'connected':
                time.sleep(0.1)
                
            codec = client.negotiated_codec
            sample_rate = client.audio_sample_rate
            
            print(f"Negotiated Codec: {codec}")
            print(f"Sample Rate: {sample_rate} Hz")
            print(f"Expected Quality: {'HD' if codec == 'G722' else 'Standard'}")
            
            if codec == "G722":
                print("✅ High quality G.722 active!")
            else:
                print("ℹ️  Using standard quality codec")
                print("   Consider enabling G.722 on your server")
                
        finally:
            client.disconnect()
    
    if __name__ == "__main__":
        test_codec_quality()

Troubleshooting Codec Issues
-----------------------------

No G.722 Support
~~~~~~~~~~~~~~~~~

If G.722 is not being negotiated:

1. **Check server configuration** - Ensure G.722 is enabled
2. **Check extension settings** - Extension must allow G.722
3. **Network issues** - Some NAT devices block G.722

.. code-block:: python

    # Force codec preference (server must support it)
    # This is done automatically by SimpleSIP
    
Audio Quality Issues
~~~~~~~~~~~~~~~~~~~~

For poor audio quality:

1. **Check sample rate** - Must match codec (8kHz vs 16kHz)
2. **Buffer size** - Use 20ms audio chunks (160/320 samples)
3. **Network jitter** - Enable jitter buffer on server

.. code-block:: python

    # Monitor audio levels
    def audio_callback(pcm_data, format_type):
        if format_type == 'pcm':
            import numpy as np
            samples = np.frombuffer(pcm_data, dtype=np.int16) 
            rms = np.sqrt(np.mean(samples**2))
            print(f"Audio level: {20 * np.log10(rms):.1f} dB")
    
    client.set_audio_callback(audio_callback, 'pcm')

Best Practices
--------------

1. **Use G.722 when possible** - Significantly better quality
2. **Match sample rates** - 16kHz for G.722, 8kHz for G.711
3. **Monitor codec negotiation** - Check what was actually negotiated  
4. **Test with different servers** - Some have better G.722 support
5. **Consider network bandwidth** - All supported codecs use 64kbps

The codec choice significantly impacts audio quality. G.722 provides much clearer, more natural-sounding audio compared to traditional G.711 codecs.