#!/usr/bin/env python3
"""
Asterisk Codec Capability Tester
Sends diagnostic SDP offers to test what codecs the server supports
"""

from simplesip import SimpleSIPClient
import time
import threading

def codec_test():
    client = SimpleSIPClient("1004", "ba5cc9c1a2b8632caf467b326e9e27e6", "10.128.50.210")
    
    try:
        print("🔍 Testing Asterisk codec support...")
        print("=" * 50)
        
        # Connect to server
        client.connect()
        
        # Wait for registration
        time.sleep(2)
        
        # Send OPTIONS request to query capabilities
        print("\n📋 1. Querying server capabilities...")
        client.query_server_capabilities()
        time.sleep(2)
        
        # Make test call with comprehensive codec offer
        print("\n📋 2. Testing codec negotiation with comprehensive offer...")
        
        # Temporarily override SDP generation for diagnostic
        original_method = client._generate_sdp_offer
        client._generate_sdp_offer = lambda: original_method(diagnostic=True)
        
        # Make a test call
        client.make_call("1002")
        
        # Wait to see what gets negotiated
        timeout = 15
        start_time = time.time()
        
        while (time.time() - start_time) < timeout and client.running:
            if client.negotiated_codec:
                print(f"\n✅ Server negotiated: {client.negotiated_codec} (PT {client.negotiated_payload_type})")
                break
            time.sleep(0.5)
        
        if not client.negotiated_codec:
            print("\n❌ No codec negotiated within timeout")
        
        # Hang up
        if client.call_id:
            client.hangup_call()
            
        time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        client.disconnect()

def show_asterisk_commands():
    print("\n" + "=" * 50)
    print("🔧 ASTERISK CLI COMMANDS TO CHECK CODEC SUPPORT:")
    print("=" * 50)
    print("1. Connect to Asterisk CLI:")
    print("   sudo asterisk -r")
    print()
    print("2. Check available codecs:")
    print("   core show codecs")
    print()
    print("3. Check SIP codec configuration:")
    print("   sip show settings | grep -i codec")
    print("   sip show settings | grep -i allow")
    print()
    print("4. For PJSIP (newer Asterisk):")
    print("   pjsip show codecs")
    print("   pjsip show endpoint 1004")
    print()
    print("5. Check configuration files:")
    print("   /etc/asterisk/sip.conf")
    print("   /etc/asterisk/pjsip.conf")
    print()
    print("Look for:")
    print("   allow=g722")
    print("   disallow=all")
    print("   allow=g722,ulaw,alaw")

if __name__ == "__main__":
    show_asterisk_commands()
    print("\n" + "=" * 50)
    print("🧪 RUNNING CODEC CAPABILITY TEST")
    print("=" * 50)
    
    try:
        codec_test()
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")