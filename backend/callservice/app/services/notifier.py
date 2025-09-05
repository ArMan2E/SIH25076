# backend/app/services/notifier.py
import os
from pathlib import Path
import json
from gtts import gTTS
import requests

TW_SID = os.environ.get("TW_SID")
TW_TOKEN = os.environ.get("TW_TOKEN")
TW_FROM = os.environ.get("TW_FROM")
TTS_HOST = os.environ.get("TTS_HOST") or "http://localhost:8000/static/tts"

def serialize_sources(sources):
    return json.dumps(sources)

def save_tts(to_number: str, text: str, lang: str = "ml"):
    """
    Save TTS mp3 under backend/app/static/tts/ so FastAPI can serve it.
    Returns (filepath, url).
    """
    folder = Path("backend/app/static/tts")
    folder.mkdir(parents=True, exist_ok=True)
    fname = f"tts_{to_number.replace('+','')}.mp3"
    filepath = folder / fname
    try:
        # gTTS expects language codes like 'ml' for Malayalam
        tts = gTTS(text=text, lang=lang)
        tts.save(str(filepath))
    except Exception as e:
        # fallback: write a small silent file or re-raise
        print("[TTS] gTTS error:", e)
        raise
    play_url = f"{TTS_HOST}/{fname}"
    return str(filepath), play_url

def send_sms_stub(to, message):
    # stub or Twilio
    if TW_SID and TW_TOKEN and TW_FROM:
        from twilio.rest import Client
        client = Client(TW_SID, TW_TOKEN)
        client.messages.create(body=message, from_=TW_FROM, to=to)
        return True
    else:
        print("[SMS STUB] To:", to)
        print(message)
        return False
