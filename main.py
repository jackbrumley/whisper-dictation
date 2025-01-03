import pyaudio
import wave
import keyboard
import threading
import requests
import tkinter as tk
import time
import pyautogui
import screeninfo
import os
from PIL import Image
import pystray
from pystray import MenuItem as item
import sys

# Global variables
running = True
restart = False

# Load configuration path
local_appdata = os.getenv('LOCALAPPDATA')
config_path = os.path.join(local_appdata, 'WhisperDictation', 'config.ini')
config_dir = os.path.dirname(config_path)
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

# Custom icon path
ICON_PATH = "assets/icon.ico"

def type_text(text, output_mode, typing_speed):
    if output_mode.lower() == 'instant':
        pyautogui.write(text)
    else:
        pyautogui.typewrite(text, interval=typing_speed)

def main():
    global running, restart

    running = True
    restart = False

    # Read configuration from file
    config = {}

    try:
        with open(config_path, 'r') as config_file:
            for line in config_file:
                line = line.strip()
                if line and '=' in line:  # Ensure the line has content and is properly formatted
                    key, value = map(str.strip, line.split('=', 1))
                    config[key] = value
    except FileNotFoundError:
        print("Config file not found. Please ensure it exists at:", config_path)
        sys.exit(1)

    WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"
    WHISPER_API_KEY = config.get('WHISPER_API_KEY', 'your_api_key_here')

    PIXELS_FROM_BOTTOM = int(config.get('PIXELS_FROM_BOTTOM', 100))
    KEYBOARD_SHORTCUT = config.get('KEYBOARD_SHORTCUT', 'ctrl+shift+alt')
    TYPING_SPEED_INTERVAL = float(config.get('TYPING_SPEED_INTERVAL', 0.025))
    OUTPUT_MODE = config.get('OUTPUT_MODE', 'typed')

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = os.path.join(local_appdata, 'WhisperDictation', 'temp_audio.wav')

    def exit_app(icon, item):
        global running
        running = False
        icon.stop()

    def record_audio():
        print("Recording audio...")  # Debug
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []

        try:
            while keyboard.is_pressed(KEYBOARD_SHORTCUT):
                data = stream.read(CHUNK)
                frames.append(data)
        finally:
            print("Stopping audio stream...")  # Debug
            stream.stop_stream()
            stream.close()
            audio.terminate()

        print("Saving recorded audio to file.")  # Debug
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as waveFile:
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(frames))

    def transcribe_audio():
        try:
            print("Starting transcription process...")  # Debug
            with open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
                headers = {"Authorization": f"Bearer {WHISPER_API_KEY}"}
                files = {'file': (WAVE_OUTPUT_FILENAME, audio_file, 'audio/wav')}
                data = {'model': 'whisper-1'}
                print(f"Sending request to Whisper API with headers: {headers}, data: {data}")  # Debug
                response = requests.post(WHISPER_API_URL, headers=headers, files=files, data=data)
                print(f"Response Status Code: {response.status_code}")  # Debug
                print(f"Response Text: {response.text}")  # Debug
                response.raise_for_status()
                text = response.json().get("text", "")
                print(f"Transcription result: {text}")  # Debug
                return text
        except Exception as e:
            print(f"Error during transcription: {e}")  # Debug
            return "[Error in transcription]"
        finally:
            if os.path.exists(WAVE_OUTPUT_FILENAME):
                print("Removing temporary audio file.")  # Debug
                os.remove(WAVE_OUTPUT_FILENAME)

    def show_status_window(status):
        screen = screeninfo.get_monitors()[0]
        screen_width = screen.width
        screen_height = screen.height

        window_width = 300
        window_height = 100
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = screen_height - window_height - PIXELS_FROM_BOTTOM

        window = tk.Tk()
        window.title("Whisper Dictation")
        window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        window.attributes("-topmost", True)
        if os.path.exists(ICON_PATH):
            window.iconbitmap(ICON_PATH)
        label = tk.Label(window, text=status, font=("Helvetica", 16))
        label.pack(expand=True)
        window.update()
        return window

    def dictation_process():
        while running:
            if keyboard.is_pressed(KEYBOARD_SHORTCUT):
                print("Shortcut detected, starting dictation process...")  # Debug
                window = show_status_window("Recording...")
                record_audio()

                window.destroy()
                window = show_status_window("Transcribing...")

                try:
                    transcription = transcribe_audio()
                except requests.exceptions.RequestException as e:
                    print(f"Request exception: {e}")  # Debug
                    transcription = "[Error in transcription]"

                window.destroy()

                if transcription:
                    print("Typing transcription...")  # Debug
                    type_text(transcription, OUTPUT_MODE, TYPING_SPEED_INTERVAL)
            else:
                time.sleep(0.1)

    dictation_thread = threading.Thread(target=dictation_process)
    dictation_thread.daemon = True

    def setup_tray_icon():
        def open_config_editor(icon, item):
            print("Opening configuration editor...")  # Debug
            os.system(f'notepad.exe "{config_path}"')

        image = Image.open(ICON_PATH) if os.path.exists(ICON_PATH) else None
        menu = (
            item('Edit Config', open_config_editor),
            item('Quit', exit_app),
        )
        icon = pystray.Icon("WhisperDictation", image, "Whisper Dictation", menu)
        dictation_thread.start()
        icon.run()

    setup_tray_icon()

    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
