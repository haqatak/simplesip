API Reference
=============

SimpleSIPClient
---------------

The main SIP client class for making and receiving calls.

Constructor
~~~~~~~~~~~

.. code-block:: python

    SimpleSIPClient(username, password, server, port=5060)

**Parameters:**

- ``username`` (str): SIP username/extension
- ``password`` (str): SIP password  
- ``server`` (str): SIP server hostname or IP
- ``port`` (int): SIP server port (default: 5060)

**Example:**

.. code-block:: python

    client = SimpleSIPClient("1001", "password", "192.168.1.100")

Methods
~~~~~~~

connect()
^^^^^^^^^

Connect to the SIP server and register.

.. code-block:: python

    client.connect()

**Returns:** True if connection successful, False otherwise

**Raises:**

- ``ConnectionError``: If unable to connect to server
- ``AuthenticationError``: If credentials are invalid

make_call(destination)
^^^^^^^^^^^^^^^^^^^^^^

Initiate an outbound call.

.. code-block:: python

    client.make_call("1234")

**Parameters:**

- ``destination`` (str): Number or extension to call

**Returns:** True if call initiation successful

send_audio(audio_data)
^^^^^^^^^^^^^^^^^^^^^^

Send audio data via RTP.

.. code-block:: python

    client.send_audio(pcm_data)

**Parameters:**

- ``audio_data`` (bytes): PCM audio data

set_audio_callback(callback_func, format='pcmu')
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Set callback for received audio.

.. code-block:: python

    def audio_callback(data, format_type):
        # Handle audio data
        pass

    client.set_audio_callback(audio_callback, 'pcm')

**Parameters:**

- ``callback_func``: Function to call with audio data
- ``format`` (str): 'pcm' or 'pcmu'

send_dtmf(digit)
^^^^^^^^^^^^^^^^

Send DTMF tone.

.. code-block:: python

    client.send_dtmf('1')

**Parameters:**

- ``digit`` (str): DTMF digit (0-9, \*, #, A-D)

hangup_call()
^^^^^^^^^^^^^

End the current call.

.. code-block:: python

    client.hangup_call()

disconnect()
^^^^^^^^^^^^

Disconnect from SIP server.

.. code-block:: python

    client.disconnect()

Properties
~~~~~~~~~~

call_state
^^^^^^^^^^

Current call state (CallState enum).

.. code-block:: python

    if client.call_state == CallState.CONNECTED:
        print("Call is active")

negotiated_codec
^^^^^^^^^^^^^^^^

The codec negotiated for the current call.

.. code-block:: python

    print(f"Using codec: {client.negotiated_codec}")

remote_rtp_info
^^^^^^^^^^^^^^^

Remote RTP endpoint (IP, port) tuple.

.. code-block:: python

    if client.remote_rtp_info:
        ip, port = client.remote_rtp_info
        print(f"Remote RTP: {ip}:{port}")

CallState Enum
--------------

Call state enumeration:

- ``IDLE`` - No active call
- ``INVITING`` - Outbound call initiated  
- ``RINGING`` - Remote party ringing
- ``CONNECTED`` - Call connected
- ``STREAMING`` - Audio streaming active

Audio Codecs
------------

Supported Codecs
~~~~~~~~~~~~~~~~

- **G.722** - High quality 16kHz audio (payload type 9)
- **PCMU** - μ-law 8kHz audio (payload type 0)  
- **PCMA** - A-law 8kHz audio (payload type 8)

Codec Negotiation
~~~~~~~~~~~~~~~~~

The client automatically negotiates the best codec:

1. G.722 (preferred)
2. PCMU (fallback)
3. PCMA (alternative)

Basic Example
-------------

.. code-block:: python

    from simplesip import SimpleSIPClient
    import time

    client = SimpleSIPClient("1001", "password", "sip.example.com")
    client.connect()
    client.make_call("1002")

    # Wait for connection
    while client.call_state.value != 'connected':
        time.sleep(0.1)

    print("Call connected!")
    input("Press Enter to hang up...")
    client.disconnect()

Audio Streaming Example
-----------------------

.. code-block:: python

    import pyaudio
    from simplesip import SimpleSIPClient

    def audio_callback(pcm_data, format_type):
        # Play received audio
        output_stream.write(pcm_data)

    # Set up audio
    audio = pyaudio.PyAudio()
    input_stream = audio.open(format=pyaudio.paInt16, channels=1, 
                             rate=8000, input=True, frames_per_buffer=160)
    output_stream = audio.open(format=pyaudio.paInt16, channels=1,
                              rate=8000, output=True, frames_per_buffer=160)

    # Set up SIP client
    client = SimpleSIPClient("1001", "password", "sip.example.com")
    client.set_audio_callback(audio_callback, 'pcm')

    client.connect()
    client.make_call("1002")

    # Audio loop
    while client.call_state.value in ['connected', 'streaming']:
        audio_data = input_stream.read(160)
        client.send_audio(audio_data)
        time.sleep(0.02)

    # Cleanup
    client.disconnect()
    input_stream.close()
    output_stream.close()
    audio.terminate()