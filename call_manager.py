from voice_agent import VoiceAgent

class CallManager:
    def __init__(self, sip_client):
        self.sip_client = sip_client
        self.calls = {}

    def on_incoming_call(self, call_id, from_uri):
        """
        Handles incoming calls by creating a new VoiceAgent for each call.
        """
        if call_id in self.calls:
            print(f"Call {call_id} already exists.")
            return

        print(f"New incoming call from {from_uri} with call ID {call_id}")
        agent = VoiceAgent(self.sip_client)
        self.calls[call_id] = agent
        agent.start()

    def on_call_ended(self, call_id):
        """
        Cleans up when a call ends.
        """
        if call_id in self.calls:
            print(f"Call {call_id} ended.")
            del self.calls[call_id]
