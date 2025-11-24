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



def add_event(event = None, title = None, start = None, end = None, path='streamlit/cal_events.json'):
    """Prende in input un evento (dizionario) o i singoli dati, imposta il datetime corretto, e aggiorna il json"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if(event):
        start_formatted = datetime.strptime(event.get('start').get('dateTime'), "%Y-%m-%dT%H:%M:%S")
        end_formatted = datetime.strptime(event.get('end').get('dateTime'), "%Y-%m-%dT%H:%M:%S")
        event = {
            "title": event.get('summary'),
            "start": start_formatted,
            "end": end_formatted
        }

    elif(title and start and end):
        start_formatted = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        end_formatted = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
        event = {
            "title": title,
            "start": start_formatted,
            "end": end_formatted
        }

    else:
        print(f'''
            ERROR: failed to save event, passed empty arguments:
            event: {event},
            title: {title},
            start: {start},
            end: {end}.
        ''')

    data.append(event)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        return True