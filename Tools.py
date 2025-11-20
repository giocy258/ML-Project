# agent_tools.py
import datetime
import json
from calendarapi import accesso, read_calendar, add_calendar, delete_calendar
# Assumo che tu abbia accesso al modulo parser o debba replicarne la logica qui
# import parser 

def tool_list_upcoming_events(days: int = 7):
    """
    Strumento per leggere gli eventi dei prossimi N giorni.
    L'LLM userà questo per rispondere a "cosa ho da fare questa settimana?".
    """
    creds = accesso() # 1. Le credenziali sono gestite INTERNAMENTE
    
    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(days=days)
    
    date_info = {
        "start": start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d")
    }
    
    # Chiamiamo la tua funzione originale
    events = read_calendar(creds, date_info)
    
    # Restituiamo una stringa o JSON semplificato all'LLM
    if not events:
        return "Nessun evento trovato."
    
    # Semplifichiamo l'output per risparmiare token all'LLM
    output_list = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        summary = e.get("summary", "Senza titolo")
        output_list.append(f"- {start}: {summary}")
        
    return "\n".join(output_list)

def tool_add_event(summary: str, start_datetime: str, end_datetime: str, location: str = ""):
    """
    Aggiunge un evento al calendario.
    Args:
        summary: Titolo dell'evento.
        start_datetime: Data inizio in formato ISO (es. 2025-11-20T15:00:00)
        end_datetime: Data fine in formato ISO.
        location: Luogo (opzionale).
    """
    creds = accesso()
    
    # 2. Costruiamo il dizionario che la tua 'add_calendar' si aspetta
    # Nota: Qui stiamo simulando quello che farebbe il tuo 'parser.format_event'
    event_dict = {
        "summary": summary,
        "location": location,
        "start": {"dateTime": start_datetime, "timeZone": "Europe/Rome"},
        "end": {"dateTime": end_datetime, "timeZone": "Europe/Rome"},
        # Se il tuo 'add_calendar' si aspetta chiavi specifiche per il parser, mettile qui
    }
    
    # Nota: la tua add_calendar originale chiama parser.format_event(event).
    # Assicurati che event_dict sia compatibile con quella chiamata, 
    # oppure modifica add_calendar per accettare un oggetto evento standard di Google.
    try:
        add_calendar(creds, event_dict)
        return f"Evento '{summary}' aggiunto correttamente."
    except Exception as e:
        return f"Errore durante l'aggiunta dell'evento: {str(e)}"
    

# TOOLS DA METTERE IN AGENTPY

from langchain.tools import tool
from calendarapi import accesso, add_calendar
import datetime


@tool
def add_event_tool(summary:str, start_time:str, end_time:str):
    creds=accesso()
    event_dict={...}
    add_calendar(creds,event_dict)
    return "fatto"
tools=[add_event_tool]
