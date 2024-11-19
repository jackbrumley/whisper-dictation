import pyaudio
import wave
import keyboard
import threading
import requests
import tkinter as tk
import time
import pyautogui
import screeninfo
import configparser
import os
from PIL import Image
import pystray
from pystray import MenuItem as item
import sys
from tkinter import messagebox

# Global variables
running = True
restart = False

# Load configuration path
local_appdata = os.getenv('LOCALAPPDATA')
config_path = os.path.join(local_appdata, 'WhisperDictation', 'config.ini')
config_dir = os.path.dirname(config_path)
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

# Global config parser
config = configparser.ConfigParser()

# Custom icon path
ICON_PATH = "assets/icon.ico"

def setup_config():
    global config, restart

    # Create default config if not exists
    if not os.path.exists(config_path):
        config['API'] = {'WHISPER_API_KEY': 'your_api_key_here'}
        config['Window'] = {'PIXELS_FROM_BOTTOM': '100'}
        config['Shortcut'] = {'KEYBOARD_SHORTCUT': 'ctrl+shift+alt'}
        config['Typing'] = {'TYPING_SPEED_INTERVAL': '0.025'}
        with open(config_path, 'w') as configfile:
            config.write(configfile)
    else:
        config.read(config_path)

    # GUI to modify config values
    def save_config():
        config['API']['WHISPER_API_KEY'] = api_key_entry.get()
        config['Window']['PIXELS_FROM_BOTTOM'] = pixels_entry.get()
        config['Shortcut']['KEYBOARD_SHORTCUT'] = shortcut_entry.get()
        config['Typing']['TYPING_SPEED_INTERVAL'] = typing_speed_entry.get()
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        messagebox.showinfo("Config Saved", "Configuration saved successfully!")
        restart = True
        root.destroy()

    def cancel_config():
        restart = False
        root.destroy()

    # Create the GUI window
    root = tk.Tk()
    root.title("Whisper Dictation Setup")
    root.geometry("400x300")

    # API Key
    tk.Label(root, text="Whisper API Key:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    api_key_entry = tk.Entry(root, width=40)
    api_key_entry.insert(0, config['API']['WHISPER_API_KEY'])
    api_key_entry.grid(row=0, column=1, padx=10, pady=10)

    # Pixels from bottom
    tk.Label(root, text="Pixels from Bottom:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    pixels_entry = tk.Entry(root, width=40)
    pixels_entry.insert(0, config['Window']['PIXELS_FROM_BOTTOM'])
    pixels_entry.grid(row=1, column=1, padx=10, pady=10)

    # Keyboard Shortcut
    tk.Label(root, text="Keyboard Shortcut:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
    shortcut_entry = tk.Entry(root, width=40)
    shortcut_entry.insert(0, config['Shortcut']['KEYBOARD_SHORTCUT'])
    shortcut_entry.grid(row=2, column=1, padx=10, pady=10)

    # Typing Speed Interval
    tk.Label(root, text="Typing Speed Interval:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
    typing_speed_entry = tk.Entry(root, width=40)
    typing_speed_entry.insert(0, config['Typing']['TYPING_SPEED_INTERVAL'])
    typing_speed_entry.grid(row=3, column=1, padx=10, pady=10)

    # Save button
    tk.Button(root, text="Save", command=save_config).grid(row=4, column=1, pady=20, sticky='e')

    # Cancel button
    tk.Button(root, text="Cancel", command=cancel_config).grid(row=4, column=0, pady=20, sticky='w')

    root.mainloop()

def main():
    global running, restart, config

    running = True
    restart = False

    # Load configuration from config file
    if not os.path.exists(config_path):
        setup_config()
        config.read(config_path)
        if not restart:
            sys.exit()

    config.read(config_path)

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
    WAVE_OUTPUT_FILENAME = os.path.join(local_appdata, 'WhisperDictation', 'temp_audio.wav')

    def exit_app(icon, item):
        global running
        running = False
        icon.stop()

    def open_settings(icon, item):
        global running, restart
        running = False
        restart = True
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
        if os.path.exists(ICON_PATH):
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
        image = Image.open(ICON_PATH) if os.path.exists(ICON_PATH) else None
        menu = (item('Settings', open_settings), item('Quit', exit_app),)
        icon = pystray.Icon("WhisperDictation", image, "Whisper Dictation", menu)
        dictation_thread.start()
        icon.run()

    # Keep the main thread alive with system tray icon
    setup_tray_icon()
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

    if restart:
        setup_config()
        main()

if __name__ == "__main__":
    main()
