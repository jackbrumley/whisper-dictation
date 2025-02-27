# Windows Voice-to-Text Dictation using OpenAI Whisper

A simple voice-to-text dictation app for **Windows 10/11** using OpenAI's Whisper API.

While the built-in Windows 10/11 Voice Typing tool provides basic functionality, its accuracy can be inconsistent. This project aimed to create a superior solution—a system-wide voice-to-text application capable of transcribing speech within any text box. Key goals included simplicity, affordability, and reliability. Commercial alternatives, such as Dragon Naturally Speaking, offer robust features but often come with a high price tag.

OpenAI's Whisper model, renowned for its accuracy and utilized in features like voice input for ChatGPT's mobile app, offers a compelling alternative through its readily available and cost-effective API. This application uses the Open AI Whisper API to deliver accurate, affordable, and system-wide voice dictation on Windows that is functionally the same as the built-in Windows 10/11 Voice Typing tool but far more accurate and reliable. 

![Voice-to-Text Dictation](assets/icon256x256.png)

## Download

Latest version: [Download](https://github.com/jackbrumley/whisper-dictation/raw/main/bin/whisper-dictation.exe)

## Quick Start

Easily convert speech to text in any application using this tool. Ensure you have an OpenAI API key and sufficient credit. **Ensure you have a working microphone and it is set at your default device.**

### Setup

1. **Sign up or log in to OpenAI:** Use the links below to access your OpenAI account or create one if you don't have one already: [Sign up](https://platform.openai.com/signup/) | [Log in](https://platform.openai.com/account/api-keys)

2. **Generate an API Key:** In the Dashboard, go to the "API Keys" section and click "Create new secret key".  Copy this key somewhere safe; you'll need it shortly.  *(Important:  Treat your API key like a password. Do not share it publicly.)*

3. **Add Credit to Your Account:** Transcriptions require a small amount of credit.  Go to the "Billing" section of your OpenAI Dashboard. Add a payment method and add credit (even $5 will last a while).

4. **Configure the Application:**

   - **Run the Executable:** Double-click `whisper-dictation.exe` to launch the application.  A notepad document (`config.ini`) will open.
   - **Enter Your API Key:**  In `config.ini`, find the line `WHISPER_API_KEY = your_api_key_here`. Replace `your_api_key_here` with the API key you copied earlier.
   - **Save the Configuration:** Save the `config.ini` file and close it.
   - **Relaunch the App:** Close and reopen `whisper-dictation.exe` for the changes to take effect.


5. **Start Using Voice-to-Text:**

   - **The App Runs in the System Tray:** After launching, the app icon will appear in the system tray (bottom-right corner of your screen, near the clock).
   - **Trigger Dictation:** The default trigger key combination is `CTRL+SHIFT+ALT`. Hold down these keys and start speaking into your microphone.
   - **Stop Dictation:** Release the `CTRL+SHIFT+ALT` keys to stop recording.  The app will send your voice to OpenAI for transcription, and the transcribed text will appear where your cursor is active. 



### Autorun at Startup/Login

To have the application start automatically when your login to Windows:

1. **Open the Run dialog** (`Win + R`), type `shell:startup`, and press **Enter**.
2. **Right-click** in the folder and select **New > Shortcut**.
3. **Browse to** wherever you are storing your **whisper-dictation.exe** file and click next.
4. Give the shortcut file and name and click **Finish**.

The application should now start automatically when your reboot your computer and login.

## More Details

For more in-depth information and setup details, please refer to the [Project Documentation](https://github.com/jackbrumley/whisper-dictation/blob/main/Project.md).