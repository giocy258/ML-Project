import json
from requests import Response
from typing import List, Dict

def format_for_google_calendar_simple(event: Dict) -> Dict:
    """
    Formatta i dati di un evento in un dizionario compatibile con l'API di Google Calendar.
    Lavora solo sui campi di base: data, orario e descrizione.

    Args:
        event (dict): Dizionario contenente i dettagli minimi dell'evento:
                      - "start" (str): Data e ora di inizio in formato ISO 8601
                      - "end" (str): Data e ora di fine in formato ISO 8601
                      - "title" (str): Il titolo principale (usato come 'summary')
                      - "tooltip" (str): Il testo completo del tooltip (usato come 'description')

    Returns:
        dict: Dizionario formattato per l'uso con l'API di Google Calendar
    """
    
    # Estrae Data e Orario direttamente dai campi start e end
    start_time = event['start']
    end_time = event['end']
    
    # Usa il titolo principale per il summary e il tooltip completo per la descrizione
    summary = event.get('title', 'Evento senza titolo')
    description = event.get('tooltip', 'Nessuna descrizione disponibile.')
    
    # Imposta un colore di default (ad esempio, '8' per grigio chiaro)
    color = "8" 
    
    event_details = {
        'summary': summary,
        'location': '',  # La location è vuota, ma è un campo atteso da GCal
        'description': description,
        "colorId": color,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Europe/Rome',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/Rome',
        },
        "reminders": {
            "useDefault": False,
        }
    }
    return event_details


def parse_json_simple(json_data: List[Dict]) -> List[Dict]:
    """
    Elabora una lista di eventi, applica il filtro e formatta per Google Calendar (versione semplice).

    Args:
        json_data (list): Lista di dizionari che rappresentano gli eventi.

    Returns:
        list: Una lista di dizionari formattati per Google Calendar.
    """
    parsed_events = []
    for event in json_data:
        # Filtro: scarta l'evento se l'id è 0 o se la materia contiene "SOSPENSIONE DIDATTICA"
        if event.get("id") == 0 or event.get("title", "").strip().startswith("SOSPENSIONE DIDATTICA"):
            continue

        # Formatta l'evento utilizzando solo i campi di base 
        # (start, end, title, tooltip) e ignora la logica complessa del tooltip.
        if "tooltip" in event and "start" in event and "end" in event:
            parsed_event = format_for_google_calendar_simple(event)
            parsed_events.append(parsed_event)
            
    return parsed_events


def write_json_simple(response: Response):
    """
    Scrive gli eventi formattati (versione semplice) in un file JSON.
    """
    with open("calendar_simple.json", "w", encoding="utf-8") as json_file:
        json.dump(
            parse_json_simple(response.json()), 
            json_file, indent=4, ensure_ascii=False
            )


# Le funzioni originali sono state mantenute ma non sono utilizzate nella logica "simple"

# def parse_json(json_data: list) -> list: ...
# def parse_tooltip(tooltip: str) -> dict: ...
# def format_event(event: dict) -> dict: ...
# def write_json(response: Response): ...
# def read_json(nome_file): ...