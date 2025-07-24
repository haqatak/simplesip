SimpleSIP Documentation
=======================

SimpleSIP is a pure Python SIP (Session Initiation Protocol) client library with RTP audio streaming capabilities.

Features
--------

* **Pure Python** - No external SIP libraries required
* **Multiple Codecs** - Supports G.722 (HD audio), PCMU, and PCMA codecs  
* **Real-time Audio** - RTP audio streaming with jitter buffer
* **Easy to Use** - Simple API for making and receiving calls
* **Authentication** - SIP Digest authentication support
* **NAT Friendly** - Handles NAT traversal and port discovery

Quick Start
-----------

.. code-block:: python

    from simplesip import SimpleSIPClient
    
    # Create client
    client = SimpleSIPClient("username", "password", "sip.example.com")
    
    # Connect and make call
    client.connect()
    client.make_call("1234")
    
    # Keep call active
    while client.call_state.value != 'idle':
        time.sleep(1)
    
    client.disconnect()

Installation
------------

.. code-block:: bash

    pip install simplesip
    
    # For audio support
    pip install simplesip[audio]

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   quickstart
   api
   examples
   codecs

API Reference
-------------

.. toctree::
   :maxdepth: 2
   
   api/simplesip

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`