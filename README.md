# Whisper-Dictation

Voice-to-text dictation app for Windows using OpenAI's Whisper API.

**You need an OpenAI API key and sufficient credit on your account for this to work!**

This application runs in your system tray, waiting for a trigger keypress (CTRL+SHIFT+ALT by default). It uses your default microphone to record voice input until you release the trigger keys. The recording is sent to OpenAI's Whisper model for transcription, and the text is either typed out character by character or pasted instantly where your cursor is active, based on your configuration.

## What It Does

1. Waits in the system tray for the configured shortcut key to be pressed.
2. Records audio using your default microphone.
3. Sends the audio to OpenAI's Whisper API for transcription.
4. Types or pastes the transcription into the active application based on the selected output mode.
5. Displays status windows for recording and transcribing, positioned dynamically based on user settings.

## Features

- **Configurable Output Modes**: Choose between "typed" (character-by-character simulation) or "instant" (essentailly copy/paste). Note: The "instant" mode is not currently implimented.
- **Custom Shortcut Key**: Allows you to configure the key combination for triggering the dictation process.
- **Status Window**: Displays recording and transcription progress with adjustable positioning.
- **Tray Icon Menu**: Edit configuration and exit the app easily from the system tray.

## Installation

### Prerequisite: Install Python

1. Download and install Python from the [official Python website](https://www.python.org/downloads/). Make sure to add Python to your system's PATH during installation.
2. Verify that Python is installed by running the following command in your terminal or command prompt:

```bash
python --version
```

### Install Required Packages

To install the required Python packages, run the following command:

**Note:** If you encounter any permissions issues, you may need to run this command as an administrator.

```bash
pip install pyaudio keyboard requests pyautogui screeninfo pillow pystray
```

## Downloading the Application

To download the latest version of the application, click [here](https://github.com/jackbrumley/whisper-dictation/archive/refs/heads/main.zip) to download a ZIP file of the repository.

1. Extract the contents of the ZIP file to a folder on your computer.
2. Navigate to the extracted folder and run the script (or double-click `main.py`).

## Running the Application


To run the script, double-click the `main.py` file to launch the application or use the following command:

```bash
python main.py
```

## Creating a Startup Shortcut

If you would like the application to automatically start when you log in:

1. Right-click on `main.py` and select **Create Shortcut**.
2. Press `Win + R` to open the Run dialog.
3. Type `shell:startup` and press Enter to open the Startup folder.
4. Move the shortcut you created into the Startup folder.
5. The application will now launch automatically when you log in.

## Configuration File

The configuration file (`config.ini`) is created in the user's AppData directory on the first run of the script. You can also edit the configuration directly through the "Edit Config" option in the system tray menu.

Path:
`C:\Users\<user>\AppData\Local\WhisperDictation\config.ini`

### Configuration Options

Below are the options available in the configuration file:

- **WHISPER_API_KEY**  
  **Required**: Your OpenAI API key (you must replace the placeholder key).

- **PIXELS_FROM_BOTTOM**  
  Adjusts how far the status windows are positioned from the bottom of the screen (default: `80`).

- **KEYBOARD_SHORTCUT**  
  The keyboard combination used to start recording (default: `ctrl+shift+alt`).

- **TYPING_SPEED_INTERVAL**  
  The delay (in seconds) between each character when outputting transcribed text in "typed" mode. Adjust as needed for performance.

- **OUTPUT_MODE**  
  Determines how the text is output:  
  - `typed`: Simulates typing by outputting characters one at a time.  
  - `instant`: Outputs the text using a much faster typing simulation. **Note:** When set to "instant," the application outputs a message in the console: "Future functionality"

## Setting Up Your OpenAI API Key

To use this application, you need a valid OpenAI account to create an API key. Additionally, you must have credit on your OpenAI account. While the cost of usage is generally inexpensive, you need to ensure your account has sufficient credit for the API requests.

1. Visit the [OpenAI API page](https://platform.openai.com/signup/) to create an account if you don’t already have one.
2. Once your account is created, log in to the [OpenAI Dashboard](https://platform.openai.com/account/api-keys).
3. Navigate to the API Keys section and generate a new API key.
4. Copy the generated API key.
5. Open the `config.ini` file (you can use the "Edit Config" option in the system tray menu) and replace the placeholder `your_api_key_here` with your new API key.

### Adding Credits to Your OpenAI Account

1. In your OpenAI Dashboard, navigate to the Billing section.
2. Add a payment method or pre-purchase credits to ensure your API requests are processed.
3. Check your account usage and remaining credits regularly to avoid interruptions.

## Notes

- Make sure your API key is valid and has sufficient credit.
- This application works best in environments with a stable microphone setup.

## Credits

Originally forked from:  
https://github.com/Snuffypot11/Whisper-Dictation

With the following improvements:

- Added instant text output mode.
- Improved configuration management via taskbar menu.
- Enhanced debugging and error handling.
- Added a dynamic positioning system for status windows.
- Included user-friendly alerts for missing API keys or configurations.

