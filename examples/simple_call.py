#!/usr/bin/env python3
"""
Simple Call Example - SimpleSIP

This example demonstrates how to make a basic SIP call using SimpleSIP.
"""

from simplesip import SimpleSIPClient
import time
import sys

def main():
    # Configuration
    USERNAME = "1001"  # Your SIP username
    PASSWORD = "your_password"  # Your SIP password  
    SERVER = "192.168.1.100"  # Your SIP server IP
    DESTINATION = "1002"  # Number to call
    
    # Create SIP client
    client = SimpleSIPClient(USERNAME, PASSWORD, SERVER)
    
    try:
        print("SimpleSIP - Simple Call Example")
        print("=" * 40)
        
        # Connect to SIP server
        print(f"Connecting to SIP server {SERVER}...")
        if not client.connect():
            print("❌ Failed to connect to SIP server")
            return 1
        
        print("✅ Connected to SIP server")
        
        # Make the call
        print(f"📞 Calling {DESTINATION}...")
        if not client.make_call(DESTINATION):
            print("❌ Failed to initiate call")
            return 1
        
        print("📤 Call initiated, waiting for response...")
        
        # Wait for call to connect
        timeout = 30  # seconds
        start_time = time.time()
        
        while client.call_state.value not in ['connected', 'streaming']:
            # Check for timeout
            if time.time() - start_time > timeout:
                print("⏰ Call timeout - no response")
                break
                
            # Check if call failed
            if client.call_state.value == 'idle':
                print("❌ Call failed or was rejected")
                break
                
            # Show current state
            print(f"📋 Call state: {client.call_state.value}")
            time.sleep(1)
        
        # Check if call connected
        if client.call_state.value in ['connected', 'streaming']:
            print("✅ Call connected successfully!")
            print("🔊 Call is active...")
            
            # Keep call active for demonstration
            call_duration = 10  # seconds
            print(f"⏱️  Keeping call active for {call_duration} seconds")
            
            for i in range(call_duration):
                status = client.get_call_status()
                print(f"📊 Status: {status['state']} | Duration: {i+1}s")
                time.sleep(1)
            
            print("🔚 Ending call...")
            client.end_call()
            print("✅ Call ended successfully")
        
    except KeyboardInterrupt:
        print("\n🛑 Call interrupted by user")
        client.end_call()
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        
    finally:
        # Always disconnect
        print("🔌 Disconnecting from server...")
        client.disconnect()
        print("👋 Goodbye!")

if __name__ == "__main__":
    sys.exit(main() or 0)