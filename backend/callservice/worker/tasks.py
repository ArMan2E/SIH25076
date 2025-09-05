from .celery_app import celery
import tempfile
import os
from ..app.services.asr import transcribe_audio
from ..app.services.llm_rag import generate_answer
from ..app.services.notifier import send_sms, make_call_with_tts
from ..app.models import save_query_record
from ..app.utils import download_url_to_file

@celery.task(bind=True)
def process_incoming_call(self, recording_url, caller):
    try:
        tmpf = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        download_url_to_file(recording_url, tmpf)
        # Transcribe
        text, conf = transcribe_audio(tmpf, language='ml')
        if not text:
            answer = "ക്ഷമിക്കണം, നിങ്ങളുടെ ശബ്ദം തിരിച്ചറിയാനായില്ല. ദയവായി വീണ്ടും വിളിക്കൂ അല്ലെങ്കിൽ SMS വഴി അറിയിക്കുക."
            send_sms(caller, answer)
            make_call_with_tts(caller, answer)
            save_query_record(caller, text, answer, [], confidence=conf)
            return {"status": "failed_transcribe"}
        # Generate answer
        answer, sources = generate_answer(text, caller)
        # Store in DB
        rec = save_query_record(caller, text, answer, sources, confidence=conf)
        # Notify
        send_sms(caller, answer)
        make_call_with_tts(caller, answer)
        return {"status": "ok", "id": rec.id}
    except Exception as e:
        print("Error processing call:", e)
        return {"status":"error","error":str(e)}
