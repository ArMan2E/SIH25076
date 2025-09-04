# test_llm_cli.py
import subprocess
import json

def ask_llm_cli(question: str) -> str:
    """
    Ask TinyLlama offline via Ollama CLI and return the answer.
    """
    try:
        # Run the Ollama CLI
        result = subprocess.run(
            ["ollama", "run", "tinyllama:1.1b", question],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR] {e.stderr.strip()}"


if __name__ == "__main__":
    q = "Answer the following question in Malayalam: പാഡി ഫീൽഡിനുള്ള കാലാവസ്ഥ എന്താണ് ഇന്ന്?"
    ans = ask_llm_cli(q)
    print("LLM Response:", ans)
