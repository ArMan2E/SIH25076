import os
from ..utils import ensure_wav_16khz
import tempfile

def transcribe_audio(filepath, language='ml'):
    """
    Offline-first: Whisper (openai-whisper). language code 'ml' for Malayalam.
    Returns (transcript, confidence)
    """
    try:
        import whisper
        model_name = os.environ.get('WHISPER_MODEL','small')
        model = whisper.load_model(model_name)
        # ensure 16k wav for better accuracy
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        ensure_wav_16khz(filepath, tmp)
        res = model.transcribe(tmp, language=language)
        text = res.get('text','').strip()
        # confidence not provided reliably; use avg_logprob if present
        confidence = res.get('avg_logprob', 0)
        return text, float(confidence or 0.0)
    except Exception as e:
        # fallback to Google STT if configured
        if os.environ.get('USE_GOOGLE_STT','0') == '1':
            try:
                from google.cloud import speech_v1p1beta1 as speech
                client = speech.SpeechClient()
                with open(filepath,'rb') as f:
                    content = f.read()
                audio = speech.RecognitionAudio(content=content)
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code='ml-IN',
                    enable_automatic_punctuation=True
                )
                resp = client.recognize(config=config, audio=audio)
                if not resp.results:
                    return "", 0.0
                transcript = " ".join(r.alternatives[0].transcript for r in resp.results)
                conf = resp.results[0].alternatives[0].confidence
                return transcript, float(conf)
            except Exception:
                return "", 0.0
        else:
            return "", 0.0
