from faster_whisper import WhisperModel
import pyttsx3
import argostranslate.package, argostranslate.translate
from ollama import Ollama  # TinyLlama offline via Ollama

# --------------------------
# 1. Transcribe audio (local dialect)
# --------------------------
def transcribe_audio(file_path):
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, info = model.transcribe(file_path, task="translate")  # translate -> English
    text = " ".join([segment.text for segment in segments])
    return text

# --------------------------
# 2. Translate text (optional, if needed)
# --------------------------
def translate_text(text, from_lang="ml", to_lang="en"):
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang_obj = next(filter(lambda l: l.code == from_lang, installed_languages))
    to_lang_obj = next(filter(lambda l: l.code == to_lang, installed_languages))
    translation = from_lang_obj.get_translation(to_lang_obj)
    return translation.translate(text)

# --------------------------
# 3. Query TinyLlama offline
# --------------------------
def query_llm(question):
    # Ollama TinyLlama offline
    response = Ollama.run("tinyllama:1.1b", question)
    return response

# --------------------------
# 4. Text-to-Speech
# --------------------------
def speak_text(text, lang="en"):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# --------------------------
# 5. Full pipeline
# --------------------------
def farmer_assistant_pipeline(audio_file_path):
    print("Transcribing audio...")
    english_text = transcribe_audio(audio_file_path)
    print("Text (English):", english_text)

    print("Querying LLM...")
    answer = query_llm(english_text)
    print("Answer (English):", answer)

    print("Speaking answer...")
    speak_text(answer)

if __name__ == "__main__":
    audio_file = "examples/sample_malayalam.wav"  # replace with your farmer audio
    farmer_assistant_pipeline(audio_file)
