import pyttsx3

print("Testing...")
engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.say("Hello sir, Jarvis is working!")
engine.runAndWait()
engine.stop()
print("Done!")