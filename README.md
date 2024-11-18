# Whisper-Dictation
Voice to text dictation app for Windows using OpenAI's Whisper API

**You need an OpenAI API key for this to work!**

98% written with the help of AI

A simple app that runs in your tray waiting for a trigger keypress (CTRL+SHIFT+ALT by default), using your default microphone it records your voice until you release the trigger keys, it will then be sent to OpenAI's Whisper model and the text is sent back and typed out wherever your cursor is active.

## To run

Install dependancies (list to come)

run main.py

## Config.ini
### WHISPER_API_KEY =

**Required** you need an OpenAI API account and available credit

### PIXELS_FROM_BOTTOM = 100

Status windows when recording and transcribing is displayed in the center of the main monitor, this value changes how far from the bottom of the screen the window is.

### KEYBOARD_SHORTCUT = crtl+shift+alt

The keyboard combination you need to hold to record.

### TYPING_SPEED_INTERVAL = 0.025

The delay between characters when the transcribed text is being output, making this too small can result in missing characters. 0.025 is the sweet spot in my testing.
