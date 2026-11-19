import speech_recognition as sr
import webbrowser
import pyttsx3
import ollama
import urllib.parse
import pywhatkit
import os
import subprocess
import time
from thefuzz import fuzz

# Initialize only the recognizer globally
recognizer = sr.Recognizer()

# SET YOUR PROJECT PATH HERE
PROJECTS_ROOT = os.path.join(os.path.expanduser("~"), "Desktop", "Jarvis_Projects")

# ──────────────────────────────────────────────
# KEY FIX: Fresh engine every call — no global engine, no threading
def speak(text):
    print(f"Jarvis: {text}")
    try:
        engine = pyttsx3.init()                        # no 'sapi5' arg
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        del engine                                     # fully destroy COM object
    except Exception as e:
        print(f"[Speak Error]: {e}")

def listen_once(timeout=6, phrase_limit=6):
    try:
        time.sleep(1)                                  # reduced from 4s → 1s
        with sr.Microphone() as source:
            recognizer.energy_threshold = 400
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening for input...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            result = recognizer.recognize_google(audio).lower()
            print(f"[Heard]: {result}")
            if "jarvis" in result or len(result.strip()) == 0:
                print("[Ignored]: Heard own voice, waiting for real input...")
                return None
            return result
    except Exception as e:
        print(f"[Listen Error]: {e}")
        return None

def offline_ai(prompt, model="qwen2.5-coder"):
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

def create_folder_project(folder_name, description):

    # STEP 1: Create folder
    os.makedirs(PROJECTS_ROOT, exist_ok=True)
    target_path = os.path.join(PROJECTS_ROOT, folder_name)
    os.makedirs(target_path, exist_ok=True)
    print(f"[Path]: {target_path}")
    speak(f"Folder {folder_name} created.")

    # STEP 2: Generate code
    speak("Generating your code, please wait sir...")

    prompt = f"""You are an expert web developer.
Create a complete, beautiful, single-file HTML portfolio website for: {description}

Requirements:
- All CSS must be internal (inside <style> tag)
- All JavaScript must be internal (inside <script> tag)
- Use modern design: dark theme, smooth animations, gradient accents
- Include sections: Hero, About, Skills, Projects, Contact
- Use Google Fonts (Poppins or similar)
- Make it fully responsive (mobile friendly)
- Add smooth scroll and hover effects
- Return ONLY the raw HTML code. No explanation. No markdown. No code blocks.
"""
    code_content = offline_ai(prompt, model="qwen2.5-coder")

    # STEP 3: Save file
    file_path = os.path.join(target_path, "index.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code_content)
    print(f"[Saved]: {file_path}")
    speak("Code saved successfully.")

    # STEP 4: Open in VS Code
    try:
        subprocess.Popen(["code", target_path], shell=True)
        speak("Opening in VS Code.")
    except Exception as e:
        speak("Could not open VS Code.")
        print(f"[VS Code Error]: {e}")

    # STEP 5: Open in Browser
    try:
        time.sleep(2)
        full_path = os.path.abspath(file_path)
        webbrowser.open(f"file:///{full_path}")
        speak("Showing in browser. Enjoy sir!")
    except Exception as e:
        speak("Could not open browser.")
        print(f"[Browser Error]: {e}")

def processCommand(command):
    command = command.lower()

    if "play" in command:
        song = command.split("play")[-1].strip()
        speak(f"Playing {song} on YouTube")
        pywhatkit.playonyt(song)

    elif "open youtube" in command:
        if "search" in command:
            search_query = command.split("search")[-1].strip()
            encoded_query = urllib.parse.quote(search_query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            speak(f"Searching {search_query} on YouTube")
            webbrowser.open(url)
        else:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")

    elif "open google" in command:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "open linkedin" in command:
        speak("Opening LinkedIn")
        webbrowser.open("https://www.linkedin.com")

    elif "open flipkart" in command:
        if "search" in command:
            search_query = command.split("search")[-1].strip()
            encoded_query = urllib.parse.quote(search_query)
            url = f"https://www.flipkart.com/search?q={encoded_query}"
            speak(f"Searching {search_query} on Flipkart")
            webbrowser.open(url)
        else:
            speak("Opening Flipkart")
            webbrowser.open("https://www.flipkart.com")

    elif ("create a folder" in command or "make a folder" in command or
          "create a project" in command or "make a project" in command or
          "creative folder" in command):

        speak("Sure sir! What should I name the project folder?")
        name = listen_once(timeout=6)
        if not name:
            speak("Sorry sir, I couldn't hear the folder name. Please say it again.")
            return
        folder_name = name.strip().replace(" ", "_")

        speak(f"What should I build inside {folder_name}?")
        desc = listen_once(timeout=8, phrase_limit=10)
        if not desc:
            speak("Sorry sir, I couldn't hear the description. Please say it again.")
            return

        create_folder_project(folder_name, desc)

    else:
        reply = offline_ai(command, model="llama3")
        speak(reply)

if __name__ == "__main__":

    print(f"\n Projects will be saved to: {PROJECTS_ROOT}\n")

    speak("Initializing Jarvis...")

    while True:
        try:
            with sr.Microphone() as source:
                print("\n[Waiting for wake word: 'Jarvis']")
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
                text = recognizer.recognize_google(audio).lower()
                print(f"[Wake]: {text}")

                if "jarvis" in text:
                    command = text.replace("jarvis", "").strip()

                    if command:
                        processCommand(command)
                    else:
                        speak("Yes sir, How can I help you?")
                        follow_up = listen_once(timeout=5)
                        if follow_up:
                            processCommand(follow_up)
                        else:
                            speak("Sorry sir, I didn't catch that. Please say it again.")

        except Exception as e:
            print(f"[Loop Error]: {e}")   # now shows errors instead of hiding them
            continue