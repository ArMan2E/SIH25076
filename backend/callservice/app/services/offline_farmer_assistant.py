# offline_farmer_assistant.py
import subprocess
from pathlib import Path

# Faster Whisper for offline speech-to-text
from faster_whisper import WhisperModel

# Argos Translate for offline translation
import argostranslate.package
import argostranslate.translate

# -----------------------------
# 1️⃣ Transcription (local dialect -> English)
# -----------------------------
def transcribe_file_to_english(file_path: str, model_size="tiny"):
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    model = WhisperModel(model_size, device="cpu", compute_type="int8")  # CPU-friendly
    segments, info = model.transcribe(file_path, task="translate")
    return " ".join([s.text for s in segments]).strip()


# -----------------------------
# 2️⃣ LLM Query (TinyLlama offline)
# -----------------------------
def ask_llm(question_en: str) -> str:
    """
    Ask TinyLlama offline via Ollama CLI
    """
    cmd = ["ollama", "run", "tinyllama:1.1b", question_en]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[LLM ERROR] {e.stderr}"

# -----------------------------
# 3️⃣ Translation (English -> Local)
# -----------------------------
def translate_text(text: str, target_lang="ml") -> str:
    """
    target_lang: ISO code, e.g. "ml"=Malayalam, "hi"=Hindi
    """
    installed_languages = argostranslate.translate.get_installed_languages()
    to_lang = next((l for l in installed_languages if l.code == target_lang), None)
    if not to_lang:
        return text  # fallback to English if language not installed

    from_lang = installed_languages[0]  # assume English
    translated = from_lang.translate(text, to_lang)
    return translated

# -----------------------------
# 4️⃣ Complete Pipeline
# -----------------------------
def farmer_assistant_pipeline(audio_file_path: str, source_lang="ml"):
    """
    Full offline pipeline: Audio -> English -> LLM -> Local language
    """
    # 1. Transcribe
    question_en = transcribe_file_to_english(audio_file_path)

    # 2. LLM
    answer_en = ask_llm(question_en)

    # 3. Translate back
    answer_local = translate_text(answer_en, target_lang=source_lang)
    return answer_local

# -----------------------------
# 5️⃣ Test Run
# -----------------------------
if __name__ == "__main__":
    sample_file = "examples/sample_malayalam.wav"
    try:
        answer = farmer_assistant_pipeline(sample_file, source_lang="ml")
        print("Final Answer (local language):", answer)
    except Exception as e:
        print("[ERROR]", e)
