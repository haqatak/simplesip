Quick Start Guide
=================

This guide will help you get started with SimpleSIP quickly.

Installation
------------

Install SimpleSIP using pip:

.. code-block:: bash

    pip install simplesip

For audio streaming capabilities, install with audio dependencies:

.. code-block:: bash

    pip install simplesip[audio]

Basic Usage
-----------

Making a Call
~~~~~~~~~~~~~

.. code-block:: python

    from simplesip import SimpleSIPClient
    import time
    
    # Create SIP client
    client = SimpleSIPClient(
        username="your_username",
        password="your_password", 
        server="your.sip.server.com"
    )
    
    try:
        # Connect to SIP server
        client.connect()
        
        # Make a call
        client.make_call("destination_number")
        
        # Wait for call to connect
        while client.call_state.value not in ['connected', 'streaming']:
            time.sleep(0.1)
            
        print("Call connected!")
        
        # Keep call active
        input("Press Enter to hang up...")
        
    finally:
        client.disconnect()

Audio Streaming
~~~~~~~~~~~~~~~

.. code-block:: python

    import pyaudio
    import threading
    from simplesip import SimpleSIPClient
    
    # Audio configuration
    CHUNK = 160
    FORMAT = pyaudio.paInt16
    CHANNELS = 1  
    RATE = 8000
    
    def audio_callback(pcm_data, format_type):
        """Handle received audio"""
        # Play audio through speakers
        output_stream.write(pcm_data)
    
    # Set up audio
    audio = pyaudio.PyAudio()
    input_stream = audio.open(format=FORMAT, channels=CHANNELS, 
                             rate=RATE, input=True, frames_per_buffer=CHUNK)
    output_stream = audio.open(format=FORMAT, channels=CHANNELS,
                              rate=RATE, output=True, frames_per_buffer=CHUNK)
    
    # Create and configure client
    client = SimpleSIPClient("username", "password", "server.com")
    client.set_audio_callback(audio_callback, 'pcm')
    
    try:
        client.connect()
        client.make_call("1234")
        
        # Audio transmission loop
        while client.call_state.value in ['connected', 'streaming']:
            audio_data = input_stream.read(CHUNK)
            client.send_audio(audio_data)
            time.sleep(0.02)  # 20ms
            
    finally:
        client.disconnect()
        input_stream.close()
        output_stream.close()
        audio.terminate()

Configuration Options
---------------------

The SimpleSIPClient accepts several configuration options:

.. code-block:: python

    client = SimpleSIPClient(
        username="1001",           # SIP username
        password="secret",         # SIP password  
        server="192.168.1.100",   # SIP server IP/hostname
        port=5060                 # SIP server port (default: 5060)
    )

Codec Support
-------------

SimpleSIP supports multiple audio codecs:

* **G.722** - High quality 16kHz audio (preferred)
* **PCMU (G.711 μ-law)** - Standard 8kHz audio
* **PCMA (G.711 A-law)** - Standard 8kHz audio

The client automatically negotiates the best available codec with the server.

Error Handling
--------------

.. code-block:: python

    try:
        client.connect()
        client.make_call("1234")
    except ConnectionError:
        print("Failed to connect to SIP server")
    except Exception as e:
        print(f"Call failed: {e}")
    finally:
        client.disconnect()

Next Steps
----------

* Check out the :doc:`api` documentation for detailed method descriptions
* See :doc:`examples` for more usage examples  
* Learn about :doc:`codecs` for audio quality optimization