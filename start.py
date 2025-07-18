# from bridge.server import BetterSIPCall
from bridge.sdk import SIPClient
import time


# if __name__ == "__main__":
    
#     sip_client = BetterSIPCall(
#         sip_user="1004",
#         sip_pass="ba5cc9c1a2b8632caf467b326e9e27e6",
#         sip_domain="10.128.50.219",
#         sip_proxy_ip="10.128.50.219",
#         sip_port=5060,
#         rtp_port=4000
#     )
    
#     try:
#         if sip_client.register():
#             print("Registration successful!")
            
#             target_number = "1002"
#             if sip_client.start_call(target_number):
#                 print(f"Call to {target_number} started successfully!")
                
#                 time.sleep(30)
                
#                 sip_client.hangup()
#             else:
#                 print("Failed to start call")
#         else:
#             print("Registration failed")
            
#     except KeyboardInterrupt:
#         print("Interrupted by user")
#     finally:
#         sip_client.close()
#         print("SIP client closed")


client = SIPClient("1004", "ba5cc9c1a2b8632caf467b326e9e27e6", "10.128.50.219")

try:
    # Connect and register
    client.connect()
    
    # Make a call (will automatically handle authentication)
    client.make_call("1002")
    
    # Keep running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.disconnect()
except Exception as e:
    print(f"Error: {e}")
    client.disconnect()
