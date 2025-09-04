import os
from pathlib import Path
from twilio.rest import Client
from gtts import gTTS

# Twilio credentials (optional)
TW_SID = os.environ.get('TW_SID')
TW_TOKEN = os.environ.get('TW_TOKEN')
TW_FROM = os.environ.get('TW_FROM')


def send_sms(to, message):
    """Send SMS if Twilio creds exist, else print stub."""
    if TW_SID and TW_TOKEN and TW_FROM:
        client = Client(TW_SID, TW_TOKEN)
        client.messages.create(body=message, from_=TW_FROM, to=to)
        return True
    else:
        print("[SMS STUB] To:", to)
        print(message)
        return False


def save_tts(to: str, text: str):
    """
    Save a Malayalam TTS MP3 file into backend/app/static/tts/.
    Returns the filepath.
    """
    folder = "backend/app/static/tts"
    os.makedirs(folder, exist_ok=True)

    fname = f"tts_{to.replace('+','')}.mp3"
    filepath = os.path.join(folder, fname)

    try:
        tts = gTTS(text=text, lang="ml")  # 'ml' = Malayalam
        tts.save(filepath)
        print(f"[CALL TTS] Saved TTS file: {filepath}")
    except Exception as e:
        print(f"[CALL TTS ERROR] {e}")

    return filepath
