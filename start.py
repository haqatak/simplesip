from simplesip import SimpleSIPClient
from call_manager import CallManager
import time

# --- SIP Configuration ---
# Replace with your SIP server details
USERNAME = "1004"
PASSWORD = "ba5cc9c1a2b8632caf467b326e9e27e6"
SERVER = "10.128.50.210"


def main():
    """
    Main function to run the voice agent.
    """
    try:
        # Initialize the SIP client
        client = SimpleSIPClient(USERNAME, PASSWORD, SERVER)

        # Initialize the Call Manager
        call_manager = CallManager(client)

        # Set the call manager for the client
        client.call_manager = call_manager

        # Connect to the SIP server
        client.connect()

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if 'client' in locals() and client.running:
            client.disconnect()


if __name__ == "__main__":
    main()
