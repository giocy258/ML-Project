# Tools.py
import datetime
from zoneinfo import ZoneInfo
from calendarapi import accesso, read_calendar, add_calendar, delete_calendar
from trova_un_buco import trova_slot_alternativo

def tool_list_upcoming_events(days: int = 7):
    """
    Elenca gli eventi in calendario per i prossimi N giorni.
    """
    creds = accesso()
    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(days=days)
    
    date_info = {
        "start": start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d")
    }
    
    # Importante: Assicurati che read_calendar in calendarapi.py non abbia filtri attivi
    events = read_calendar(creds, date_info)
    
    if not events:
        return "Nessun evento trovato nei prossimi giorni."
    
    output_list = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        summary = e.get("summary", "Senza titolo")
        output_list.append(f"- {start}: {summary}")
        
    return "\n".join(output_list)

def tool_find_availability(duration_minutes: int, days_to_check: int = 5) -> str:
    """
    Trova il primo slot libero. Da usare quando l'utente chiede 'quando sono libero?'.
    """
    creds = accesso()
    return trova_slot_alternativo(
        creds=creds, 
        duration_minutes=duration_minutes, 
        search_days=days_to_check,
        buffer_minutes=30
    )

def tool_safe_add_event(summary: str, start_iso: str, end_iso: str):
    """
    [PRINCIPALE] Aggiunge un evento solo se lo slot è libero.
    Se occupato, suggerisce alternative.
    """
    creds = accesso()
    
    try:
        start_dt = datetime.datetime.fromisoformat(start_iso)
        end_dt = datetime.datetime.fromisoformat(end_iso)
        # Aggiunge timezone se mancante (default Rome)
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=ZoneInfo("Europe/Rome"))
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=ZoneInfo("Europe/Rome"))
    except ValueError:
        return "Errore: Formato data non valido. Usa ISO (YYYY-MM-DDTHH:MM:SS)."

    # Controlla disponibilità
    date_info = {
        "start": start_dt.date().isoformat(),
        "end": end_dt.date().isoformat()
    }
    existing_events = read_calendar(creds, date_info) 
    
    is_busy = False
    for event in existing_events:
        ev_start_str = event['start'].get('dateTime')
        ev_end_str = event['end'].get('dateTime')
        
        if ev_start_str and ev_end_str: # Considera solo eventi con orario
            ev_start = datetime.datetime.fromisoformat(ev_start_str)
            ev_end = datetime.datetime.fromisoformat(ev_end_str)
            
            # Logica sovrapposizione: (StartA < EndB) and (EndA > StartB)
            if (start_dt < ev_end) and (end_dt > ev_start):
                is_busy = True
                break
    
    if is_busy:
        duration = int((end_dt - start_dt).total_seconds() / 60)
        # Cerca alternative a partire dalla data del conflitto
        suggerimento = trova_slot_alternativo(
            creds, 
            duration_minutes=duration, 
            start_search_from=start_dt, # Richiede modifica in trova_un_buco.py
            search_days=3
        )
        return f"❌ Slot occupato. {suggerimento}"
    
    else:
        # Aggiunta effettiva
        event_dict = {
            "summary": summary,
            "start": {"dateTime": start_iso, "timeZone": "Europe/Rome"},
            "end": {"dateTime": end_iso, "timeZone": "Europe/Rome"},
        }
        try:
            add_calendar(creds, event_dict)
            return f"✅ Evento '{summary}' aggiunto correttamente: {start_iso}"
        except Exception as e:
            return f"Errore API: {e}"

def tool_force_add_event(summary: str, start_iso: str, end_iso: str):
    """
    [SOLO EMERGENZE] Aggiunge un evento ignorando i conflitti.
    Da usare solo su ordine esplicito dell'utente.
    """
    creds = accesso()
    event_dict = {
        "summary": summary,
        "start": {"dateTime": start_iso, "timeZone": "Europe/Rome"},
        "end": {"dateTime": end_iso, "timeZone": "Europe/Rome"},
    }
    add_calendar(creds, event_dict)
    return f"⚠️ Evento forzato aggiunto: {summary}"