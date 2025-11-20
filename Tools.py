# agent_tools.py
import datetime
import json
from calendarapi import accesso, read_calendar, add_calendar, delete_calendar
import parser 
from trova_un_buco import trova_slot_alternativo

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
    
# ... qui ci sono le altre funzioni tool_add_event, tool_list_events ...

def tool_find_availability(duration_minutes: int, days_to_check: int = 5) -> str:
    """
    Cerca il primo slot libero disponibile nel calendario per una data durata.
    Da usare quando l'utente chiede di trovare spazio per un'attività senza specificare l'ora.
    
    Args:
        duration_minutes (int): Durata dell'attività in minuti.
        days_to_check (int): Quanti giorni nel futuro controllare (default 5).
    
    Returns:
        str: Un suggerimento testuale su quando è possibile prenotare.
    """
    # 1. Recuperiamo le credenziali internamente (invisibile all'LLM)
    creds = accesso() #
    
    # 2. Chiamiamo la tua funzione di logica pura
    # Nota: puoi lasciare il buffer a 30 minuti fisso o esporlo all'LLM se necessario
    risultato = trova_slot_alternativo(
        creds=creds, 
        duration_minutes=duration_minutes, 
        search_days=days_to_check,
        buffer_minutes=30
    ) #
    
    return risultato

def tool_safe_add_event(summary: str, start_iso: str, end_iso: str):
    """
    Tenta di aggiungere un evento. Se lo slot è occupato, NON aggiunge nulla 
    e restituisce un suggerimento alternativo vicino a quella data.
    """
    creds = accesso()
    
    # 1. Controlliamo se c'è conflitto
    start_dt = datetime.datetime.fromisoformat(start_iso)
    end_dt = datetime.datetime.fromisoformat(end_iso)
    
    # Leggiamo il calendario per quel giorno specifico
    date_info = {
        "start": start_dt.date().isoformat(),
        "end": end_dt.date().isoformat()
    }
    existing_events = read_calendar(creds, date_info) #
    
    is_busy = False
    for event in existing_events:
        # Logica semplificata di sovrapposizione
        ev_start = event['start'].get('dateTime') # Necessario parsing corretto
        # ... controllo se gli orari si sovrappongono ...
        # Se si sovrappongono: is_busy = True
    
    if is_busy:
        # 2. Se occupato, cerchiamo un buco PARTENDO DA QUELLA DATA
        duration = (end_dt - start_dt).seconds // 60
        suggerimento = trova_slot_alternativo(
            creds, 
            duration_minutes=duration, 
            start_search_from=start_dt, # La modifica che abbiamo discusso
            search_days=2 # Cerca solo nei 2 giorni successivi al conflitto
        )
        return f"Impossibile aggiungere: slot occupato. {suggerimento}"
    
    else:
        # 3. Se libero, aggiungi
        add_calendar(creds, {...}) #
        return "Evento aggiunto con successo."

# TOOLS DA METTERE IN AGENTPY
'''
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
'''