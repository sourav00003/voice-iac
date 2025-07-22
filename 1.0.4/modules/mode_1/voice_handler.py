import speech_recognition as sr

def voice_to_text():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print(" Listening...")
        #audio = recognizer.listen(source)
        audio = recognizer.record(source, duration=6)

        try:
            print("Converting speech to text...")
            text = recognizer.recognize_google(audio)
            print(f" You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand your voice.")
        except sr.RequestError as e:
            print(f"Could not request results from Google API; {e}")


# Voice Confirmation for Destroy
def get_voice_confirmation():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say 'yes' to confirm destroy, or 'no' to cancel:")
        audio = recognizer.listen(source, phrase_time_limit=4)

    try:
        response = recognizer.recognize_google(audio).lower()
        print(f"You said: {response}")
        return response
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"Google API error: {e}")
        return ""
    
    