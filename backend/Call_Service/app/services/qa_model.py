# backend/app/services/qa_model.py

import os
import json
from google.generativeai import chat
from google.generativeai.client import ChatClient

# Initialize Gemini client
client = ChatClient(api_key=os.getenv("GEMINI_API_KEY"))

async def answer_query(question: str, context: str = "") -> str:
    """
    Ask Gemini Pro 2.5 Flash to answer the question in Malayalam.
    Returns the answer text.
    """
    try:
        prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer in Malayalam, short and clear."

        response = client.send_message(
            model="gemini-pro-2.5-flash",
            message=prompt,
            temperature=0.3,
            max_output_tokens=500
        )

        # Gemini response text
        answer = response.text if hasattr(response, "text") else str(response)
        return answer

    except Exception as e:
        return f"[ERROR] {e}"

def serialize_sources(sources: list) -> str:
    """
    Convert Python list to JSON string for SQLite storage.
    """
    return json.dumps(sources)

def deserialize_sources(sources_json: str) -> list:
    """
    Convert JSON string back to Python list.
    """
    try:
        return json.loads(sources_json)
    except:
        return []
