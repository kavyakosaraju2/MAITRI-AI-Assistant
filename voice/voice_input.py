import speech_recognition as sr

def listen_to_user():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("🎤 MAITRI is listening... Speak now")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣 You said: {text}")
        return text

    except sr.UnknownValueError:
        print(" Sorry, I could not understand your voice")
        return ""

    except sr.RequestError:
        print(" Speech service error")
        return ""

