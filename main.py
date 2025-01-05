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
config_path = os.path.join(local_appdata, 'whisper-dictation', 'config.ini')
config_dir = os.path.dirname(config_path)
if not os.path.exists(config_dir):
  os.makedirs(config_dir)

# Custom icon path for the system tray
ICON_PATH = "assets/icon.ico"

# Whisper API URL (set globally)
WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"

def type_text(text, output_mode, typing_speed):
  # Handles typing text instantly or character by character.
  if output_mode.lower() == 'instant':
    message = (
      "[Future Functionality] Instant mode is not implemented yet.\n"
      "Please update your config file to set OUTPUT_MODE to 'typed' instead."
    )
    print(message)
    input("Press Enter to exit...")
    sys.exit(1)
  else:
    pyautogui.typewrite(text, interval=typing_speed)

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

  def exit_app(icon, item):
    # Gracefully exits the application.
    global running
    running = False
    icon.stop()

  image = Image.open(ICON_PATH) if os.path.exists(ICON_PATH) else None
  menu = (
    item('Edit Config', open_config_editor),
    item('Quit', exit_app),
  )
  icon = pystray.Icon("whisper-dictation", image, "Whisper Dictation", menu)
  threading.Thread(target=icon.run, daemon=True).start()

def main():
  # Main function to initialize and run the application.
  global running, restart, input_ready

  running = True
  restart = False

  # Set up the system tray icon early
  setup_tray_icon()

  print("Tray icon initialized.")

  # Read or create configuration file
  config = {}
  config_created = False

  try:
    with open(config_path, 'r') as config_file:
      for line in config_file:
        line = line.strip()
        if line and '=' in line:
          key, value = map(str.strip, line.split('=', 1))
          config[key] = value
  except FileNotFoundError:
    # Create a default config file if it doesn't exist
    with open(config_path, 'w') as config_file:
      config_file.write("# API Configuration\n")
      config_file.write("WHISPER_API_KEY=your_api_key_here\n\n")
      config_file.write("# Window settings\n")
      config_file.write("PIXELS_FROM_BOTTOM=80\n\n")
      config_file.write("# Shortcut configuration\n")
      config_file.write("KEYBOARD_SHORTCUT=ctrl+shift+alt\n\n")
      config_file.write("# Typing speed\n")
      config_file.write("TYPING_SPEED_INTERVAL=0.001\n\n")
      config_file.write("# Output mode (typed or instant)\n")
      config_file.write("OUTPUT_MODE=typed\n")
    config_created = True

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

  # Check for invalid OUTPUT_MODE
  OUTPUT_MODE = config.get('OUTPUT_MODE', 'typed')
  if OUTPUT_MODE.lower() == 'instant':
    message = (
      "[Future Functionality] Instant mode is not implemented yet.\n"
      "Please update your config file to set OUTPUT_MODE to 'typed' instead."
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
  dictation_thread.start()

  try:
    while running:
      time.sleep(1)
  except KeyboardInterrupt:
    print("Exiting...")

if __name__ == "__main__":
  main()
