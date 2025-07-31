import time

class VoiceAgent:
    def __init__(self, sip_client):
        self.sip_client = sip_client
        self.sip_client.set_audio_callback(self.on_audio_received)

    def on_audio_received(self, audio_data, format):
        """Callback for when audio is received from the SIP client."""
        print(f"Received {len(audio_data)} bytes of {format} audio.")
        # In a real application, you would forward this to the LLM.
        # For now, we'll just log it.

    def send_audio(self, audio_data):
        """Sends audio data to the SIP client."""
        self.sip_client.send_audio(audio_data)

    def start(self):
        """Starts the voice agent."""
        print("Voice agent started.")
        # In a real application, you might have a loop here to handle
        # the conversation with the LLM.
        while self.sip_client.running:
            time.sleep(1)
