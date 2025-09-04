from .services.transcriber import transcribe_url
from .services.qa_model import answer_query
from .services.notifier import send_sms, save_tts
from .models import save_query_record

def handle_incoming_call_webhook(payload: dict):
    caller = payload.get("From")
    recording_url = payload.get("RecordingUrl")

    print(f"[CALL] Incoming from {caller}, recording={recording_url}")

    # 1. Transcribe
    question = transcribe_url(recording_url)
    print(f"[TRANSCRIBED] {question}")

    # 2. Get AI Answer from Ollama
    qa_result = answer_query(question)
    answer = qa_result["answer"]
    confidence = qa_result["confidence"]
    sources = qa_result["sources"]

    print(f"[AI ANSWER] {answer}")

    # 3. Save record in DB
    save_query_record(caller, question, answer, sources, confidence)

    # 4. Send SMS with answer
    send_sms(caller, f"നിങ്ങളുടെ ചോദ്യം: {question}\n\nഉത്തരം: {answer}")

    # 5. Generate TTS for call playback
    save_tts(caller, answer)
