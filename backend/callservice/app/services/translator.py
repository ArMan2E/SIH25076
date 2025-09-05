# backend/app/services/translator.py
import threading
from transformers import MarianMTModel, MarianTokenizer

# We'll lazy-load models to avoid startup delays
_lock = threading.Lock()
_models = {}

def _load_model_pair(src_tgt: str):
    """
    src_tgt like 'en-ml' or 'ml-en' maps to Helsinki models:
    en->ml: Helsinki-NLP/opus-mt-en-ml
    ml->en: Helsinki-NLP/opus-mt-ml-en
    """
    mapping = {
        "en-ml": "Helsinki-NLP/opus-mt-en-ml",
        "ml-en": "Helsinki-NLP/opus-mt-ml-en",
    }
    model_name = mapping[src_tgt]
    with _lock:
        if src_tgt not in _models:
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            _models[src_tgt] = (tokenizer, model)
    return _models[src_tgt]

def en_to_ml(text: str) -> str:
    if not text:
        return ""
    tok, model = _load_model_pair("en-ml")
    batch = tok.prepare_seq2seq_batch([text], return_tensors="pt")
    gen = model.generate(**batch, max_new_tokens=200)
    out = tok.batch_decode(gen, skip_special_tokens=True)
    return out[0].strip()

def ml_to_en(text: str) -> str:
    if not text:
        return ""
    tok, model = _load_model_pair("ml-en")
    batch = tok.prepare_seq2seq_batch([text], return_tensors="pt")
    gen = model.generate(**batch, max_new_tokens=200)
    out = tok.batch_decode(gen, skip_special_tokens=True)
    return out[0].strip()
