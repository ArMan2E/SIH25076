# backend/app/services/qa_model.py
import subprocess
import shlex
import html
import json

MODEL_NAME = "tinyllama:1.1b"   # Ollama model you have

def answer_query_english(question_en: str, timeout: int = 30) -> dict:
    """
    Send English question to local Ollama tinyllama and return answer dict:
    { "answer": "...", "confidence": 0.0, "sources": [] }
    """
    try:
        # Use subprocess to call ollama CLI. Quote question so shell doesn't mangle it.
        # Better to pass as args list for safety.
        # Note: ollama run <model> <prompt>
        proc = subprocess.run(
            ["ollama", "run", MODEL_NAME, question_en],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        out = proc.stdout.strip()
        # sometimes Ollama prints additional info; keep stdout as answer
        return {"answer": out, "confidence": 0.0, "sources": []}
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or str(e)
        return {"answer": f"[ERROR] Ollama failed: {stderr}", "confidence": 0.0, "sources": []}
    except Exception as e:
        return {"answer": f"[ERROR] {e}", "confidence": 0.0, "sources": []}
