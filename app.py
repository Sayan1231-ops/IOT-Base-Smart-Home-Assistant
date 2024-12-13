import requests
import pyttsx3  # type: ignore
import speech_recognition as sr  # type: ignore
from flask import Flask
import threading
import datetime
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Configure voice for a more human-like sound (e.g., Jervis)
def configure_voice():
    """Configures the text-to-speech engine to use a specific voice."""
    voices = engine.getProperty('voices')
    # Iterate through available voices and select a desired one
    for voice in voices:
        if "english" in voice.name.lower():  # Use an English voice (adjust as needed)
            engine.setProperty('voice', voice.id)
            break
    # Set other properties for a more natural tone
    engine.setProperty('rate', 150)  # Speed of speech (lower = slower)
    engine.setProperty('volume', 1.0)  # Volume (1.0 is max)

configure_voice()

# Flask setup for receiving motion detection request
app = Flask(__name__)

# Replace with the IP address of your ESP8266
ESP_IP = "http://192.168.0.104"  # Replace with your ESP8266’s actual IP address

# Text-to-speech function
def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()

# Voice command recognition and control
def recognize_voice_command():
    """Recognizes voice commands and executes the corresponding actions."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Recognized command: {command}")

        if "hi rabi" in command or "hello" in command:
            speak("Hi Sayan, how can I help you?")
        elif "date and time" in command or "what's the time" in command or "what's the date" in command:
            now = datetime.datetime.now()
            current_date = now.strftime("%B %d, %Y")
            current_time = now.strftime("%H:%M:%S")
            response = f"Today's date is {current_date} and the current time is {current_time}."
            speak(response)
            print(response)
        elif "fan on" in command or "turn on the fan" in command:
            turn_fan_on()
        elif "fan off" in command or "turn off the fan" in command:
            turn_fan_off()
        elif "light on" in command or "turn on the light" in command:
            turn_light_on()
        elif "light off" in command or "turn off the light" in command:
            turn_light_off()
        elif "temperature" in command or "what's the room temperature" in command:
            get_temperature()
        else:
            speak("Command not recognized. Please say something like 'turn on the fan' or 'turn off the light'.")

    except sr.UnknownValueError:
        speak("Sorry, I could not understand the audio.")
    except sr.RequestError:
        speak("Could not request results; please check your internet connection.")

# Define functions to control fan and light
def turn_fan_on():
    url = f"{ESP_IP}/fan/on"
    response = requests.get(url)
    print(response.text)
    speak("Fan turned on")

def turn_fan_off():
    url = f"{ESP_IP}/fan/off"
    response = requests.get(url)
    print(response.text)
    speak("Fan turned off")

def turn_light_on():
    url = f"{ESP_IP}/light/on"
    response = requests.get(url)
    print(response.text)
    speak("Light turned on")

def turn_light_off():
    url = f"{ESP_IP}/light/off"
    response = requests.get(url)
    print(response.text)
    speak("Light turned off")

@app.route('/motion', methods=['GET'])
def motion_detected():
    speak("Motion detected. Turning on the fan and light.")
    try:
        response = requests.get(f"{ESP_IP}/temperature")
        temp_data = response.text
        speak(f"Hi Sayan. Light and fan are now on. Current temperature is {temp_data}")
    except Exception as e:
        speak(f"Error fetching temperature data: {e}")
    return "Motion detected and action performed."

@app.route('/temperature', methods=['GET'])
def get_temperature():
    try:
        response = requests.get(f"{ESP_IP}/temperature")
        temp_data = response.text
        speak(f"The current temperature is {temp_data} degrees Celsius.")
        return temp_data
    except Exception as e:
        error_message = f"Error fetching temperature data: {e}"
        speak(error_message)
        return error_message

# Function to run Flask server
def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# Function to display the animated GIF in Tkinter
def start_gui():
    """Starts the GUI."""
    root = tk.Tk()
    root.title("Virtual Assistant - Rabi")
    root.geometry("1500x1700")
    root.configure(bg="black")

    # Create a Text widget to display print statements
    output_text = tk.Text(root, height=20, width=80, wrap=tk.WORD, bg="black", fg="white", font=("Arial", 12))
    output_text.pack(pady=20)

    # Redirect print statements to the Text widget
    sys.stdout = TextRedirector(output_text)

    # Display introduction message in the Text widget
    output_text.insert(tk.END, "Hey Sayan, I'm Raabi, your home assistant. What can I do for you today?\n")
    output_text.insert(tk.END, "If you want to control your devices, just say something like 'turn on the fan', 'turn off the light', or whatever you need, and I’ll take care of it.\n")
    output_text.yview(tk.END)  # Scroll to the bottom to show the latest text

    # Load the animated GIF
    gif_path = "D:/pdfs/Classproject/assgpro/Smart home system/BHFO.gif"
    if os.path.exists(gif_path):
        try:
            # Open the GIF using PIL
            gif_image = Image.open(gif_path)
            frames = []
            try:
                while True:
                    # Append each frame of the GIF to a list
                    frame = gif_image.copy()
                    frames.append(ImageTk.PhotoImage(frame))
                    gif_image.seek(gif_image.tell() + 1)
            except EOFError:
                pass  # End of GIF frames

            # Create a label for the animated GIF
            avatar_label = tk.Label(root, bg="black")
            avatar_label.pack(pady=20)

            # Function to update the displayed frame
            def update_frame(frame_index):
                avatar_label.config(image=frames[frame_index])
                root.after(100, update_frame, (frame_index + 1) % len(frames))  # Update every 100ms

            update_frame(0)  # Start the animation
        except Exception as e:
            print(f"Error loading avatar GIF: {e}")
            avatar_label = tk.Label(root, text="Error loading avatar image!", bg="black", fg="white")
            avatar_label.pack(pady=20)
    else:
        print("Error: Avatar GIF file not found!")
        avatar_label = tk.Label(root, text="Avatar not found!", bg="black", fg="white")
        avatar_label.pack(pady=20)

    root.mainloop()

# Custom class to redirect print statements to Tkinter Text widget
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.insert(tk.END, string)
        self.widget.yview(tk.END)  # Scroll to the bottom

    def flush(self):
        pass  # Required for compatibility, but not used.

# Function to stop the recognition
def stop_recognition():
    print("Voice recognition stopped.")
    speak("Voice recognition stopped.")

# Main function to start voice recognition
def main():
    speak("Hey Sayan, I'm Raabi, your home assistant. What can I do for you today?")
    speak("If you want to control your devices, just say something like 'turn on the fan', 'turn off the light', or whatever you need, and I’ll take care of it.")

    while True:
        recognize_voice_command()

# Run the Flask server and voice command system in parallel
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start the GUI in a separate thread
    gui_thread = threading.Thread(target=start_gui)
    gui_thread.start()

    main()
