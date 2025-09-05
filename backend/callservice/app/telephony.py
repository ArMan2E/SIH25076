# backend/app/telephony.py
import traceback
from .services.transcriber import transcribe_url_to_english
from .services.qa_model import answer_query_english
from .services.translator import en_to_ml, ml_to_en
from .services.notifier import save_tts, send_sms_stub, serialize_sources
from .models import save_query_record, SessionLocal, QueryRecord
import datetime
import os

def handle_incoming_call_webhook(payload: dict):
    """
    payload expected keys: From, RecordingUrl (or RecordingUrl in Twilio)
    This function runs in background_tasks (synchronous context)
    """
    caller = payload.get("From") or payload.get("from") or "unknown"
    recording_url = payload.get("RecordingUrl") or payload.get("recording_url") or payload.get("RecordingUrl")
    print("[CALL WEBHOOK] caller:", caller, "recording_url:", recording_url)

    try:
        if not recording_url:
            answer_ml = "ക്ഷമിക്കണം, നിങ്ങളുടെ ശബ്ദം ലഭിച്ചില്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക."
            save_path, play_url = save_tts(caller, answer_ml)
            send_sms_stub(caller, answer_ml)
            save_query_record(caller, "", answer_ml, [], confidence=0.0)
            return

        # 1) Transcribe (translate) farmer speech -> English
        english_question = transcribe_url_to_english(recording_url, model_size="tiny")
        print("[TRANSCRIBED -> ENGLISH]:", english_question)

        # If transcription empty
        if not english_question.strip():
            answer_ml = "ക്ഷമിക്കണം, ശബ്ദം വ്യക്തമല്ല. ദയവായി ചെറിയ വാചകമായി വീണ്ടും പറയുക."
            save_path, play_url = save_tts(caller, answer_ml)
            send_sms_stub(caller, answer_ml)
            save_query_record(caller, english_question, answer_ml, [], confidence=0.0)
            return

        # 2) (optional) you may do ml_to_en if you had manual transcription in Malayalam
        # english_question = ml_to_en(malayalam_text)  # not needed when whisper task=translate used

        # 3) Query offline LLM (TinyLLaMA via Ollama)
        llm_resp = answer_query_english(english_question)
        answer_en = llm_resp.get("answer", "")
        sources = llm_resp.get("sources", [])

        print("[LLM ANSWER EN]:", answer_en)

        # 4) Translate answer back to Malayalam
        try:
            answer_ml = en_to_ml(answer_en)
        except Exception as e:
            print("[TRANSLATION ERROR]", e)
            # fallback: attempt simple wrapper to ask LLM to translate
            answer_ml = answer_en  # best effort

        # 5) Generate TTS
        try:
            tts_path, play_url = save_tts(caller, answer_ml)
        except Exception as e:
            print("[TTS SAVE ERROR]", e)
            play_url = None

        # 6) Send SMS and (optionally) make call via Twilio - here stub
        sms_text = f"നിങ്ങളുടെ ചോദ്യം: \n\n{answer_ml}\n"
        send_sms_stub(caller, sms_text)

        # 7) Persist record in DB
        try:
            # depends on your models.save_query_record or SessionLocal usage
            save_query_record(caller, english_question, answer_ml, sources, confidence=llm_resp.get("confidence", 0.0))
        except Exception as e:
            print("[DB SAVE ERROR]", e)

        print("[CALL HANDLED] play_url:", play_url)
    except Exception as e:
        print("[ERROR] handle_incoming_call_webhook failed:", e)
        traceback.print_exc()
        # final fallback to user
        try:
            fallback = "ക്ഷമിക്കണം, പ്രവേശനം പരിഗണിക്കപ്പെട്ടില്ല. പിന്നീട് ശ്രമിക്കുക."
            save_tts(caller, fallback)
            send_sms_stub(caller, fallback)
            save_query_record(caller, "", fallback, [], confidence=0.0)
        except Exception:
            pass
