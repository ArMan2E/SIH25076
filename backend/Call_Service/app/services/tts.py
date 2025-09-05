import os
from gtts import gTTS
from pathlib import Path

def synthesize_text_to_file(text, outpath, lang='ml'):
    """
    Simple TTS using gTTS (uses Google TTS - requires internet) as a fallback.
    If you set USE_GOOGLE_TTS=1 and provide Google credentials, you can implement
    google-cloud-texttospeech synthesize instead.
    """
    os.makedirs(Path(outpath).parent, exist_ok=True)
    if os.environ.get('USE_GOOGLE_TTS','0') == '1':
        try:
            from google.cloud import texttospeech
            client = texttospeech.TextToSpeechClient()
            input_text = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(language_code="ml-IN", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            response = client.synthesize_speech(request={"input": input_text, "voice": voice, "audio_config": audio_config})
            with open(outpath, "wb") as f:
                f.write(response.audio_content)
            return outpath
        except Exception as e:
            # fallback to gTTS
            pass
    # gTTS fallback
    tts = gTTS(text=text, lang=lang)
    tts.save(outpath)
    return outpath
