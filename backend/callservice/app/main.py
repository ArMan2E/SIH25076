# backend/app/main.py

from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.responses import PlainTextResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel   # 👈 NEW
from .telephony import handle_incoming_call_webhook
from .models import SessionLocal, QueryRecord
from .services.qa_model import answer_query   # 👈 NEW

import os

app = FastAPI()

# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/webhook/call")
async def call_webhook(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    payload = {k: form.get(k) for k in form.keys()}
    background_tasks.add_task(handle_incoming_call_webhook, payload)
    return PlainTextResponse("<Response></Response>", status_code=200)


@app.get("/queries")
def list_queries(db: Session = Depends(get_db)):
    records = db.query(QueryRecord).order_by(QueryRecord.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "caller": r.caller,
            "question": r.question,
            "answer": r.answer,
            "sources": r.sources,
            "confidence": r.confidence,
            "created_at": r.created_at,
        }
        for r in records
    ]


@app.get("/static/tts/{fname}")
def serve_tts(fname: str):
    p = f"/tmp/tts/{fname}"
    if not os.path.exists(p):
        return PlainTextResponse("Not found", status_code=404)
    return FileResponse(p, media_type="audio/mpeg")


# 👇 NEW — API for querying directly
class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query_endpoint(req: QueryRequest, db: Session = Depends(get_db)):
    try:
        # Await the async Gemini function
        answer_text = await answer_query(req.question)

        # Store in DB
        record = QueryRecord(
            caller="api-user",
            question=req.question,
            answer=answer_text,
            sources=[],
            confidence=0.0
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return {"id": record.id, "question": req.question, "answer": answer_text}

    except Exception as e:
        return {"error": str(e)}
