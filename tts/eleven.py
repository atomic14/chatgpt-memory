import os
import elevenlabslib


class ElevenTts:
    def __init__(self):
        if os.getenv("ELEVEN_LABS_API_KEY"):
            user = elevenlabslib.ElevenLabsUser(os.getenv("ELEVEN_LABS_API_KEY"))
            self.voice = user.get_voices_by_name("Elli")[0]
        else:
            self.voice = None

    def say(self, text):
        if self.voice:
            self.voice.generate_and_play_audio(text, playInBackground=False)
