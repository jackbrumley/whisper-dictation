import pyaudio
import wave
import keyboard
import threading
import requests
import ctypes
import tkinter as tk
import time
import pyautogui
import screeninfo
import configparser
import os
from PIL import Image
import pystray
from pystray import MenuItem as item

# Load configuration from config file
config = configparser.ConfigParser()
config.read('config.ini')

# Whisper API configuration
WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"
WHISPER_API_KEY = config.get('API', 'WHISPER_API_KEY')

# Customizable settings from config file
PIXELS_FROM_BOTTOM = config.getint('Window', 'PIXELS_FROM_BOTTOM')
KEYBOARD_SHORTCUT = config.get('Shortcut', 'KEYBOARD_SHORTCUT')
TYPING_SPEED_INTERVAL = config.getfloat('Typing', 'TYPING_SPEED_INTERVAL')

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "temp_audio.wav"

# Custom icon path
ICON_PATH = "assets/icon.ico"

running = True

def exit_app(icon, item):
    global running
    running = False
    icon.stop()

# Function to record audio
def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    frames = []

    try:
        while keyboard.is_pressed(KEYBOARD_SHORTCUT):
            data = stream.read(CHUNK)
            frames.append(data)
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    # Save the recorded audio to a file
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as waveFile:
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))

# Function to transcribe audio using Whisper API
def transcribe_audio():
    try:
        with open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
            headers = {
                "Authorization": f"Bearer {WHISPER_API_KEY}"
            }
            files = {
                'file': (WAVE_OUTPUT_FILENAME, audio_file, 'audio/wav')
            }
            data = {
                'model': 'whisper-1'
            }
            response = requests.post(WHISPER_API_URL, headers=headers, files=files, data=data)
            response.raise_for_status()
            text = response.json().get("text", "")
            print(f"Transcription: {text}")
            return text
    finally:
        # Remove the temporary audio file
        if os.path.exists(WAVE_OUTPUT_FILENAME):
            os.remove(WAVE_OUTPUT_FILENAME)

# Function to type text as if typed by a keyboard
def type_text(text):
    pyautogui.typewrite(text, interval=TYPING_SPEED_INTERVAL)  # Use typing speed from config

# Function to show recording status window
def show_status_window(status):
    # Get screen information
    screen = screeninfo.get_monitors()[0]
    screen_width = screen.width
    screen_height = screen.height

    # Calculate position near the bottom center of the screen
    window_width = 300
    window_height = 100
    x_position = (screen_width // 2) - (window_width // 2)
    y_position = screen_height - window_height - PIXELS_FROM_BOTTOM

    window = tk.Tk()
    window.title("Whisper Dictation")
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    window.attributes("-topmost", True)
    window.iconbitmap(ICON_PATH)
    label = tk.Label(window, text=status, font=("Helvetica", 16))
    label.pack(expand=True)
    window.update()
    return window

# Main function to handle the dictation process
def dictation_process():
    while running:
        if keyboard.is_pressed(KEYBOARD_SHORTCUT):
            # Show recording window
            window = show_status_window("Recording...")
            
            # Record audio
            record_audio()
            
            # Update status to transcribing
            window.destroy()
            window = show_status_window("Transcribing...")
            
            # Transcribe audio
            try:
                transcription = transcribe_audio()
            except requests.exceptions.RequestException:
                transcription = "[Error in transcription]"

            # Close the window
            window.destroy()
            
            # Type out the transcribed text
            if transcription:
                type_text(transcription)

        time.sleep(0.1)

# Start the dictation process in a separate thread
dictation_thread = threading.Thread(target=dictation_process)
dictation_thread.daemon = True

# Function to setup system tray icon
def setup_tray_icon():
    image = Image.open(ICON_PATH)
    menu = (item('Quit', exit_app),)
    icon = pystray.Icon("WhisperDictation", image, "Whisper Dictation", menu)
    dictation_thread.start()
    icon.run()

# Keep the main thread alive with system tray icon
if __name__ == "__main__":
    setup_tray_icon()
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
