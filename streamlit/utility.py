import requests
import json
from datetime import datetime

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



#Prende in input i singoli dati, imposta il datetime corretto, e aggiorna il json
def add_event(title, start, end, path='streamlit/cal_events.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    start_formatted = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
    end_formatted = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
    event = {
        "title": title,
        "start": start_formatted,
        "end": end_formatted,
    }

    data.append(event)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)