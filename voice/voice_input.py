import speech_recognition as sr
import sounddevice as sd
import numpy as np


def listen_to_user(timeout=5, phrase_time_limit=8):

    recognizer = sr.Recognizer()

    sample_rate = 16000
    duration = phrase_time_limit

    print("🎤 MAITRI is listening... Speak now")

    # Record audio
    audio_np = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    audio_data = sr.AudioData(
        audio_np.tobytes(),
        sample_rate,
        2
    )

    try:
        text = recognizer.recognize_google(audio_data)

        print(f"🗣 You said: {text}")

        return text.lower()

    except sr.UnknownValueError:
        print("⚠ Could not understand audio.")
        return None

    except sr.RequestError:
        print("⚠ Speech recognition service error.")
        return None
