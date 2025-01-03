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

# Global variables for application state
running = True
restart = False
input_ready = True

# Load configuration path
local_appdata = os.getenv('LOCALAPPDATA')
config_path = os.path.join(local_appdata, 'WhisperDictation', 'config.ini')
config_dir = os.path.dirname(config_path)
if not os.path.exists(config_dir):
  os.makedirs(config_dir)

# Custom icon path for the system tray
ICON_PATH = "assets/icon.ico"

def type_text(text, output_mode, typing_speed):
  # Handles typing text instantly or character by character.
  if output_mode.lower() == 'instant':
    pyautogui.write(text)
  else:
    pyautogui.typewrite(text, interval=typing_speed)

def main():
  # Main function to initialize and run the application.
  global running, restart, input_ready

  running = True
  restart = False

  # Read or create configuration file
  config = {}

  try:
    with open(config_path, 'r') as config_file:
      for line in config_file:
        line = line.strip()
        if line and '=' in line:
          key, value = map(str.strip, line.split('=', 1))
          config[key] = value
  except FileNotFoundError:
    # Create a default config file if it doesn't exist
    print("Config file not found. Creating a default config file at:", config_path)
    default_config = {
      "WHISPER_API_KEY": "your_api_key_here",
      "PIXELS_FROM_BOTTOM": "80",
      "KEYBOARD_SHORTCUT": "ctrl+shift+alt",
      "TYPING_SPEED_INTERVAL": "0.025",
      "OUTPUT_MODE": "instant"
    }
    with open(config_path, 'w') as config_file:
      for key, value in default_config.items():
        config_file.write(f"{key}={value}\n")
    print("Default config file created. Please update it with your API key.")
    sys.exit(1)

  # API and configuration parameters
  WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"
  WHISPER_API_KEY = config.get('WHISPER_API_KEY', 'your_api_key_here')

  PIXELS_FROM_BOTTOM = int(config.get('PIXELS_FROM_BOTTOM', 100))
  KEYBOARD_SHORTCUT = config.get('KEYBOARD_SHORTCUT', 'ctrl+shift+alt')
  TYPING_SPEED_INTERVAL = float(config.get('TYPING_SPEED_INTERVAL', 0.025))
  OUTPUT_MODE = config.get('OUTPUT_MODE', 'instant')

  FORMAT = pyaudio.paInt16
  CHANNELS = 1
  RATE = 16000
  CHUNK = 1024
  WAVE_OUTPUT_FILENAME = os.path.join(local_appdata, 'WhisperDictation', 'temp_audio.wav')

  def exit_app(icon, item):
    # Gracefully exits the application.
    global running
    running = False
    icon.stop()

  def record_audio():
    # Records audio and saves it to a temporary file.
    print("Recording audio...")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    try:
      while keyboard.is_pressed(KEYBOARD_SHORTCUT):
        data = stream.read(CHUNK)
        frames.append(data)
    finally:
      print("Stopping audio stream...")
      stream.stop_stream()
      stream.close()
      audio.terminate()

    print("Saving recorded audio to file.")
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as waveFile:
      waveFile.setnchannels(CHANNELS)
      waveFile.setsampwidth(audio.get_sample_size(FORMAT))
      waveFile.setframerate(RATE)
      waveFile.writeframes(b''.join(frames))

  def transcribe_audio():
    # Sends audio to the Whisper API and returns the transcription.
    try:
      print("Starting transcription process...")
      with open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
        headers = {"Authorization": f"Bearer {WHISPER_API_KEY}"}
        files = {'file': (WAVE_OUTPUT_FILENAME, audio_file, 'audio/wav')}
        data = {'model': 'whisper-1'}
        print(f"Sending request to Whisper API with headers: {headers}, data: {data}")
        response = requests.post(WHISPER_API_URL, headers=headers, files=files, data=data)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        response.raise_for_status()
        text = response.json().get("text", "")
        print(f"Transcription result: {text}")
        return text
    except Exception as e:
      print(f"Error during transcription: {e}")
      return "[Error in transcription]"
    finally:
      if os.path.exists(WAVE_OUTPUT_FILENAME):
        print("Removing temporary audio file.")
        os.remove(WAVE_OUTPUT_FILENAME)

  def show_status_window(status):
    # Displays a temporary status window above the taskbar.
    monitors = screeninfo.get_monitors()
    main_monitor = next((m for m in monitors if m.is_primary), monitors[0])
    
    screen_width = main_monitor.width
    screen_height = main_monitor.height

    window_width = 250
    window_height = 80
    x_position = (screen_width // 2) - (window_width // 2)
    y_position = screen_height - window_height - PIXELS_FROM_BOTTOM

    window = tk.Tk()
    window.title("Whisper Dictation")
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    window.attributes("-topmost", True)

    window.resizable(False, False)

    if os.path.exists(ICON_PATH):
      window.iconbitmap(ICON_PATH)

    label = tk.Label(window, text=status, font=("Helvetica", 16), bg="white")
    label.pack(expand=True, fill=tk.BOTH)

    window.update_idletasks()
    return window

  def dictation_process():
    # Monitors the shortcut key and handles dictation.
    global input_ready
    while running:
      if input_ready:
        print(f"Waiting for input. Press and hold {KEYBOARD_SHORTCUT} to start recording...")
        input_ready = False
      if keyboard.is_pressed(KEYBOARD_SHORTCUT):
        print("Shortcut detected, starting dictation process...")
        input_ready = False
        window = show_status_window("Recording...")
        record_audio()

        window.destroy()
        window = show_status_window("Transcribing...")

        try:
          transcription = transcribe_audio()
        except requests.exceptions.RequestException as e:
          print(f"Request exception: {e}")
          transcription = "[Error in transcription]"

        window.destroy()

        if transcription:
          print("Typing transcription...")
          type_text(transcription, OUTPUT_MODE, TYPING_SPEED_INTERVAL)

        input_ready = True
      else:
        time.sleep(0.1)

  dictation_thread = threading.Thread(target=dictation_process)
  dictation_thread.daemon = True

  def setup_tray_icon():
    # Sets up the system tray icon and menu.
    def open_config_editor(icon, item):
      print("Opening configuration editor...")
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
