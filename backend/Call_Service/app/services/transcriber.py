# backend/app/services/transcriber.py

def transcribe_url(audio_url: str) -> str:
    """
    Dummy transcription service.
    In production, integrate Whisper API or your STT pipeline.
    """
    print(f"[TRANSCRIBE] Pretending to transcribe {audio_url}")
    return "sample transcribed text"
