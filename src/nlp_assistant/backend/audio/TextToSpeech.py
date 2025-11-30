import os
import sys
import time
import wave
import subprocess
from typing import Optional
from piper import PiperVoice


class VoiceAssistant:
    """
    Text-to-Speech handler using Piper and OS-native audio playback.
    """

    def __init__(self,
                 model_path: str = os.path.join("src", "nlp_assistant", "data", "models", "de_DE-thorsten_emotional-medium.onnx"),
                 debug: bool = False):
        """
        Initializes the VoiceAssistant.
        """
        self.model_path: str = model_path
        self.debug: bool = debug
        self.temp_wav_path: str = "temp_output.wav"
        self.voice: Optional[PiperVoice] = None

        if self.debug:
            print(f"* Loading Voice Model: {self.model_path}")

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at: {self.model_path}")

        self.voice = PiperVoice.load(self.model_path)

    def speak(self, text: str) -> None:
        """
        Synthesizes text to a temporary WAV file and plays it.
        """
        if not text:
            return

        if self.debug:
            print(f"* Speaking: '{text}'")

        try:
            self._synthesize_wav(text)
            self._play_wav()
        except Exception as e:
            if self.debug:
                print(f"Error during speech synthesis/playback: {e}")
        finally:
            self._cleanup()

    def _synthesize_wav(self, text: str) -> None:
        with wave.open(self.temp_wav_path, "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file)

    def _play_wav(self) -> None:
        if not os.path.exists(self.temp_wav_path):
            return

        if sys.platform.startswith("win"):
            subprocess.run(
                ["cmd", "/c", "start", "/min", "", self.temp_wav_path],
                check=True
            )
        else:
            players = [
                ["aplay", self.temp_wav_path],
                ["ffplay", "-nodisp", "-autoexit", self.temp_wav_path],
                ["paplay", self.temp_wav_path]
            ]
            for cmd in players:
                try:
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    break
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue

    def _cleanup(self) -> None:
        if os.path.exists(self.temp_wav_path):
            os.remove(self.temp_wav_path)


if __name__ == "__main__":
    print("~~~~~~ Start VoiceAssistant Direct Execution ~~~~~~")

    # Standard Pfad aus __init__ wird genutzt
    try:
        assistant = VoiceAssistant(debug=True)
        now = time.time()
        assistant.speak("Das ist ein Test.")
        took_time = time.time()-now

    except FileNotFoundError as e:
        print(f"Error: {e}")