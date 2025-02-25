# Voice-to-Text Dictation using OpenAI Whisper

A simple voice-to-text dictation app for Windows using OpenAI's Whisper API.

![Voice-to-Text Dictation](assets/icon256x256.png)

## Quick Start

Easily convert speech to text in any application using this tool. Ensure you have an OpenAI API key and sufficient credit. **Ensure you have a working microphone and it is set at your default device.**

### Download

Download the latest version: [Download](https://github.com/jackbrumley/whisper-dictation/raw/main/bin/whisper-dictation.exe)

### Setup

1. **OpenAI API Key:**

   - Sign up on the [OpenAI API page](https://platform.openai.com/signup/) if you don’t have an account.
   - Generate an API key from the [API Keys section](https://platform.openai.com/account/api-keys) in the OpenAI Dashboard.
   - Copy the API key.

2. **Edit Configuration:**
   
   - Launch the executable (`whisper-dictation.exe`) by double-clicking it.
   - In the system tray, right-click the tray icon, and select "Edit Config".
   - Replace `your_api_key_here` in the `config.ini` file with your OpenAI API key and save.

3. **Usage:**
   - The app will sit in your system tray, waiting for you to press the trigger key combination (`CTRL+SHIFT+ALT` by default).
   - Hold the trigger keys and speak into your default microphone to start recording.
   - Release the keys to stop recording and transcribe your speech into text.

### OpenAI API Key & Credit

- **API Key:** Ensure your API key is entered in the configuration file.
- **Credits:** The tool requires credit on your OpenAI account for transcriptions. You can manage credits in the Billing section of the OpenAI Dashboard. Note: Costs are minimal and $5 USD can last weeks.

### Run at Startup

To have the application start automatically when logging in:

1. Right-click `whisper-dictation.exe` and select **Create Shortcut**.
2. Open the Run dialog (`Win + R`), type `shell:startup`, and press Enter.
3. Move the shortcut to the opened Startup folder.

## More Details

For more in-depth information and setup details, please refer to the [Project Documentation](https://github.com/jackbrumley/whisper-dictation/blob/main/Project.md).
