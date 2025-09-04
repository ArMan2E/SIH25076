from pydantic import BaseModel
from typing import Optional, List

class CallWebhook(BaseModel):
    From: Optional[str]
    RecordingUrl: Optional[str]
    RecordingSid: Optional[str]
    CallSid: Optional[str]

class QueryRecordIn(BaseModel):
    caller: str
    question: str

class QueryRecordOut(BaseModel):
    id: int
    caller: str
    question: str
    answer: str
    sources: Optional[str]
    created_at: str
