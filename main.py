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
import webbrowser

KEYBOARD_SHORTCUT = "ctrl+shift+alt"  # Default value; overridden by config later
# Global variables for application state
state = {
  'running': True,
  'restart': False,
  'input_ready': True
}

# Load configuration path
local_appdata = os.getenv('LOCALAPPDATA')
config_path = os.path.join(local_appdata, 'whisper-dictation', 'config.ini')
config_dir = os.path.dirname(config_path)
if not os.path.exists(config_dir):
  os.makedirs(config_dir)

# Custom icon path for the system tray
ICON_PATH = "assets/icon.ico"

# Whisper API URL (set globally)
WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"

# Repository version file URL
REPO_VERSION_FILE_URL = "https://raw.githubusercontent.com/jackbrumley/whisper-dictation/main/version"
# GitHub repository URL
GITHUB_REPO_URL = "https://github.com/jackbrumley/whisper-dictation"

def check_for_updates():
  # Check the local and repository version files
  local_version_file = "version"

  try:
    # Read the local version
    with open(local_version_file, 'r') as file:
      local_version = file.read().strip()

    # Fetch the online version
    response = requests.get(REPO_VERSION_FILE_URL, timeout=5)
    response.raise_for_status()
    latest_version = response.text.strip()

    if latest_version != local_version:
      print(f"A new version is available: {latest_version}. You are using {local_version}.")
    else:
      print(f"You are using the latest version: {local_version}.")
  except FileNotFoundError:
    print("Local version file not found. Please ensure the 'version' file is included.")
  except requests.RequestException as e:
    print(f"Failed to check for updates: {e}")


def handle_exit_with_message(message):
  # Handles showing a message and waiting for user input before exiting
  print(message)
  input("Press Enter to exit...")
  sys.exit(1)

def setup_tray_icon():
  # Sets up the system tray icon and menu.
  def open_config_editor(icon, item):
    print("Opening configuration editor...")
    os.system(f'notepad.exe "{config_path}"')

  def view_github(icon, item):
    global KEYBOARD_SHORTCUT
    print("Opening GitHub repository...")
    print(f"Waiting for input. Press and hold {KEYBOARD_SHORTCUT} to start recording...")
    webbrowser.open(GITHUB_REPO_URL)

  def exit_app(icon, item):
    # Gracefully exits the application.
    global running
    running = False
    icon.stop()

  image = Image.open(ICON_PATH) if os.path.exists(ICON_PATH) else None
  menu = (
    item('Edit Config', open_config_editor),
    item('View GitHub', view_github),
    item('Quit', exit_app),
  )
  icon = pystray.Icon("whisper-dictation", image, "Whisper Dictation", menu)
  threading.Thread(target=icon.run, daemon=True).start()

def type_text(text, typing_speed):
  # Simulates typing text character by character
  pyautogui.typewrite(text, interval=typing_speed)

def main():
  # Main function to initialize and run the application.
  global running, restart, input_ready

  running = True
  restart = False

  # Check for updates at launch
  check_for_updates()

  # Set up the system tray icon early
  setup_tray_icon()

  print("Tray icon initialized.")

  # Read or create configuration file
  config = {}
  default_config_path = "assets/default_config.ini"
  config_created = False


  try:
    with open(config_path, 'r') as config_file:
      for line in config_file:
        line = line.strip()
        if line and '=' in line:
          key, value = map(str.strip, line.split('=', 1))
          config[key] = value
  except FileNotFoundError:
    if os.path.exists(default_config_path):
      with open(default_config_path, 'r') as default_config_file, open(config_path, 'w') as new_config_file:
        new_config_file.write(default_config_file.read())
      config_created = True
    else:
      print(f"Default configuration file not found at: {default_config_path}")
      sys.exit(1)

  print("Configuration file processed.")

  # Check for a placeholder API key and warn the user
  WHISPER_API_KEY = config.get('WHISPER_API_KEY', 'your_api_key_here')
  if config_created:
    message = (
      f"Config file not found. A default config file has been created at:\n{config_path}\n\n"
      "Please update it with your API key before running the script again."
    )
    handle_exit_with_message(message)

  if WHISPER_API_KEY == 'your_api_key_here':
    message = (
      f"The API key in the configuration file is set to the default placeholder.\n"
      f"Please update it with your OpenAI API key to use the application.\n\n"
      f"Configuration file location: {config_path}"
    )
    handle_exit_with_message(message)

  
  PIXELS_FROM_BOTTOM = int(config.get('PIXELS_FROM_BOTTOM', 100))
  KEYBOARD_SHORTCUT = config.get('KEYBOARD_SHORTCUT', 'ctrl+shift+alt')
  TYPING_SPEED_INTERVAL = float(config.get('TYPING_SPEED_INTERVAL', 0.01))

  FORMAT = pyaudio.paInt16
  CHANNELS = 1
  RATE = 16000
  CHUNK = 1024
  WAVE_OUTPUT_FILENAME = os.path.join(local_appdata, 'whisper-dictation', 'temp_audio.wav')

  print("Starting dictation thread.")

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
        response = requests.post(WHISPER_API_URL, headers=headers, files=files, data=data)
        response.raise_for_status()
        text = response.json().get("text", "")
        return text
    except Exception as e:
      print(f"Error during transcription: {e}")
      return "[Error in transcription]"
    finally:
      if os.path.exists(WAVE_OUTPUT_FILENAME):
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

    label = tk.Label(window, text=status, font=("Segoe UI", 16), bg="white")
    label.pack(expand=True, fill=tk.BOTH)

    window.update_idletasks()
    return window

  def dictation_process():
    # Monitors the shortcut key and handles dictation.
    while state['running']:
      if state['input_ready']:
        print(f"Waiting for input. Press and hold {KEYBOARD_SHORTCUT} to start recording...")
        state['input_ready'] = False
      if keyboard.is_pressed(KEYBOARD_SHORTCUT):
        print("Shortcut detected, starting dictation process...")
        state['input_ready'] = False
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
          type_text(transcription, TYPING_SPEED_INTERVAL)

        state['input_ready'] = True
      else:
        time.sleep(0.1)
      time.sleep(0.1)

  dictation_thread = threading.Thread(target=dictation_process)
  dictation_thread.daemon = True
  dictation_thread.start()

  try:
    while running:
      time.sleep(1)
  except KeyboardInterrupt:
    print("Exiting...")

if __name__ == "__main__":
  main()
