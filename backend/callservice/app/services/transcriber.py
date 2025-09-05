# backend/app/services/transcriber.py
import os
import requests
import tempfile
import time

# prefer faster-whisper; fallback to openai-whisper if not available
try:
    from faster_whisper import WhisperModel
    HAS_FAST = True
except Exception:
    HAS_FAST = False

try:
    import whisper
    HAS_WHISPER = True
except Exception:
    HAS_WHISPER = False

def download_audio(url: str) -> str:
    """
    Download recording URL to a temp file and return filepath.
    """
    r = requests.get(url, stream=True, timeout=30)
    r.raise_for_status()
    # choose suffix based on content-type or url
    content_type = r.headers.get("content-type", "")
    if "wav" in content_type or url.lower().endswith(".wav"):
        suffix = ".wav"
    elif "mpeg" in content_type or url.lower().endswith(".mp3"):
        suffix = ".mp3"
    else:
        suffix = ".wav"
    fd, path = tempfile.mkstemp(suffix=suffix, prefix="rec_")
    os.close(fd)
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return path

def _init_faster_whisper_model(model_size: str, device: str = "cpu"):
    """
    Try initializing faster-whisper with multiple compute types.
    Returns model instance or raises last exception.
    """
    compute_attempts = ["int8_float16", "int8", "float16", "float32"]
    last_exc = None
    for ct in compute_attempts:
        try:
            # If compute_type unsupported this will raise
            model = WhisperModel(model_size, device=device, compute_type=ct)
            print(f"[faster-whisper] loaded model {model_size} with compute_type={ct}")
            return model
        except Exception as e:
            last_exc = e
            print(f"[faster-whisper] compute_type {ct} failed: {e}")
    # if we got here, no compute type worked
    raise last_exc

def transcribe_file_to_english(file_path: str, model_size: str = "tiny") -> str:
    """
    Transcribe audio and *translate* to English. Returns English text.
    Uses faster-whisper if available (recommended). If faster-whisper is not usable,
    gracefully falls back to openai-whisper (if installed) or raises an error.
    model_size: "tiny","small","medium" etc.
    """
    # Try faster-whisper first
    if HAS_FAST:
        try:
            model = _init_faster_whisper_model(model_size, device="cpu")
            segments, info = model.transcribe(file_path, beam_size=5, task="translate", language=None)
            text = "".join([seg.text for seg in segments]).strip()
            return text
        except Exception as e:
            print("[transcriber] faster-whisper failed at runtime:", e)
            # fallback to openai-whisper below

    # Fallback to openai-whisper if available
    if HAS_WHISPER:
        try:
            print("[transcriber] falling back to openai-whisper")
            model = whisper.load_model(model_size)
            result = model.transcribe(file_path, task="translate")  # translate -> English
            return result.get("text", "").strip()
        except Exception as e:
            print("[transcriber] openai-whisper also failed:", e)
            raise RuntimeError(f"Both faster-whisper and openai-whisper failed: {e}")

    # Neither library is available
    raise RuntimeError("No whisper model available. Install faster-whisper or openai-whisper.")

def transcribe_url_to_english(url: str, model_size: str = "tiny") -> str:
    """
    Download URL and transcribe (translate) to English.
    """
    fpath = None
    try:
        fpath = download_audio(url)
        return transcribe_file_to_english(fpath, model_size=model_size)
    finally:
        if fpath and os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass
