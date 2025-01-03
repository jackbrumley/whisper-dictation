# Whisper-Dictation
Voice-to-text dictation app for Windows using OpenAI's Whisper API

**You need an OpenAI API key for this to work!**

98% written with the help of AI

A simple app that runs in your tray waiting for a trigger keypress (CTRL+SHIFT+ALT by default). Using your default microphone, it records your voice until you release the trigger keys. The recording is then sent to OpenAI's Whisper model, and the transcribed text is typed out wherever your cursor is active.

## Installation

To install the required Python packages, run the following command:

```bash
pip install pyaudio keyboard requests pyautogui screeninfo pillow pystray
```

## Running the Script

To run the script, use the following command:

```bash
python main.py
```

## Config.ini

The configuration file is created in the user's AppData directory by `main.py` on the first run.

Path:
`C:\Users\<user>\AppData\Local\WhisperDictation\config.ini`

The taskbar icon includes an "Edit Config" option for easy modification of the below settings in the `config.ini` file.

### WHISPER_API_KEY =

**Required**: You need an OpenAI API account and available credit.

### PIXELS_FROM_BOTTOM = 80

The status windows for recording and transcribing are displayed in the center of the main monitor. This value adjusts how far from the bottom of the screen the window is positioned.

### KEYBOARD_SHORTCUT = ctrl+shift+alt

The keyboard combination you need to hold to start recording.

### TYPING_SPEED_INTERVAL = 0.025

The delay between characters when the transcribed text is being output. Making this value too small can result in missing characters. 0.025 is the sweet spot in testing.

### OUTPUT_MODE = typed

Determines how the text is output:
- `typed`: Simulates typing by outputting characters one at a time.
- `instant`: Outputs the entire transcription instantly, as if pasted.

## Credits

Originally forked from:
https://github.com/Snuffypot11/Whisper-Dictation

With the following improvements:
- Added instant text output mode.
- Improved configuration management via taskbar menu.
- Enhanced debugging and error handling.

