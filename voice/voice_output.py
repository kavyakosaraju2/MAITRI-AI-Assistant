import pyttsx3

def speak(text):

    try:
        engine = pyttsx3.init()

        engine.setProperty('rate', 170)   # Speed
        engine.setProperty('volume', 1.0) # Volume

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("Speech error:", e)
