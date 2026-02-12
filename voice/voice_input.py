import speech_recognition as sr

def listen_to_user(timeout=3, phrase_time_limit=4):
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("🎤 MAITRI is listening... Speak now")
            r.adjust_for_ambient_noise(source, duration=0.5)

            audio = r.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        text = r.recognize_google(audio)
        print(f"🗣 You said: {text}")
        return text.lower()

    except sr.WaitTimeoutError:
        # ⏱ No speech detected
        return None

    except sr.UnknownValueError:
        # Speech unclear
        return None

    except sr.RequestError:
        print("Speech service error")
        return None


