from sqlalchemy import Column, Integer, String, Text, DateTime, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

# -------------------------------------------------------------------
# Database Configuration
# -------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./krishi.db")

# SQLite requires check_same_thread=False for multi-threaded apps
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -------------------------------------------------------------------
# Table Definitions
# -------------------------------------------------------------------
class QueryRecord(Base):
    """
    Stores each farmer's query (via call) along with system's response.
    """
    __tablename__ = "query_records"

    id = Column(Integer, primary_key=True, index=True)
    caller = Column(String(64), index=True)              # phone number
    question = Column(Text)                              # transcribed query
    answer = Column(Text)                                # generated answer
    sources = Column(Text)                               # source documents or hints
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    confidence = Column(Float, default=0.0)              # model confidence score

# -------------------------------------------------------------------
# Utility Functions
# -------------------------------------------------------------------
def init_db():
    """
    Initializes database (creates tables if not already present).
    """
    Base.metadata.create_all(bind=engine)

def save_query_record(caller, question, answer, sources, confidence=0.0):
    """
    Saves a new query/response record to the database.
    """
    db = SessionLocal()
    try:
        rec = QueryRecord(
            caller=caller,
            question=question,
            answer=answer,
            sources=str(sources),
            confidence=confidence
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec
    finally:
        db.close()
