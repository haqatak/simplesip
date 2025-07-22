# from bridge.server import BetterSIPCall
from bridge.sdk import BetterSIPClient
import time


client = BetterSIPClient("1004", "ba5cc9c1a2b8632caf467b326e9e27e6", "10.128.50.210")

# Enable SRTP for secure audio transmission


# def on_incoming_call():
#     print("Incoming call - answering...")
#     client.answer_call()

try:
    client.connect()
    
    client.make_call("1002")
    
    
    
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.disconnect()
except Exception as e:
    print(f"Error: {e}")
    client.disconnect()
