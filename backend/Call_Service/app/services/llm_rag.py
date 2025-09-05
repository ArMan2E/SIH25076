import os
from typing import Tuple, List

# Local simple RAG stub: you should replace with FAISS + sentence-transformers retrieval.
def retrieve_docs_stub(query, top_k=3):
    # For demo: read a small file or return canned text
    kb_dir = "./data/kb"
    docs = []
    if os.path.exists(kb_dir):
        for i, fname in enumerate(sorted(os.listdir(kb_dir))[:top_k]):
            with open(os.path.join(kb_dir, fname), 'r', encoding='utf8') as f:
                docs.append(f.read())
    if not docs:
        docs = [
            "ബനാനയില്‍ ലിഫ് സ്പോട്ട് ബാധയ്ക്ക് സാധാരണയായി ഫംഗസ് ആണ് കാരണം. നിയന്ത്രണത്തിന് ഫംഗിസൈഡുകൾ ഉപയോഗിക്കാം. മണ്ണ് നനുത്തതും പൂച്ചകളും നിരീക്ഷിക്കുക.",
            "പാരമ്പര്യമായി ഒരേ മരുന്നു കൂടുതലായി ഉപയോഗിക്കരുത്; ലോക്കൽ Krishi Bhavan-നെ സമീപിക്കുക."
        ]
    return docs

def generate_answer(question: str, caller: str) -> Tuple[str, List[str]]:
    docs = retrieve_docs_stub(question)
    context = "\n---\n".join(docs)
    # Prefer OpenAI if configured
    if os.environ.get('USE_OPENAI','0') == '1' and os.environ.get('OPENAI_API_KEY'):
        import openai
        openai.api_key = os.environ['OPENAI_API_KEY']
        prompt = f"""You are an agricultural assistant for Kerala farmers. Use the context to reply in Malayalam in short simple steps. Context: {context}\n\nQuestion: {question}\nAnswer:"""
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt}],
                max_tokens=300
            )
            ans = resp['choices'][0]['message']['content']
            return ans.strip(), docs
        except Exception:
            pass
    # Offline fallback: very simple template
    answer = "നിങ്ങളുടെ ചോദ്യം: " + (question or "") + "\n\nസൂചനകൾ:\n"
    answer += "- രോഗനിർണയം ഫോട്ടോ അയച്ചു തന്നാല്‍ നന്നായിരിക്കും.\n- സാധാരണയായി ഫംഗസ് ബാധയായി হলেও Krishi Bhavan-നെ സന്ദർശിക്കുക.\n"
    return answer, docs
