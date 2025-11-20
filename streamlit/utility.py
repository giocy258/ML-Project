import requests
import json

def stream_ollama(prompt, model, timeout=300):
    """
    Generatore che restituisce chunk di testo dallo stream di Ollama.
    """
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, 
               "prompt": prompt, 
               "stream": True}
    try:
        with requests.post(url, json=payload, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "response" in obj and obj["response"]:
                    yield obj["response"]
                if obj.get("done"):
                    break
    except requests.RequestException as e:
        yield f"\n\n❌ Errore di streaming da Ollama: {e}"