# Tools.py
from typing import Optional
import datetime
from zoneinfo import ZoneInfo
from .calendarapi import accesso, read_calendar, add_calendar, delete_calendar, update_calendar
from .trova_un_buco import trova_slot_alternativo

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

# Aggiungi in cima: from calendarapi import delete_calendar, update_calendar

def tool_delete_event(summary: str, date_iso: str):
    """
    Elimina un evento specifico. Richiede il titolo esatto e la data di inizio.
    """
    creds = accesso()
    
    # 1. Cerchiamo l'evento per ottenere il suo ID
    try:
        target_date = datetime.datetime.fromisoformat(date_iso)
    except ValueError:
        return "Errore: Data non valida. Usa formato ISO (YYYY-MM-DDTHH:MM:SS)."

    # Cerchiamo in una finestra stretta (giorno stesso)
    date_info = {
        "start": target_date.date().isoformat(),
        "end": target_date.date().isoformat()
    }
    
    # Nota: qui serve read_calendar senza filtri (quindi assicurati di averli tolti come detto prima)
    events = read_calendar(creds, date_info) 
    
    target_event = None
    for e in events:
        # Confronto flessibile sul nome (case insensitive)
        if summary.lower() in e.get("summary", "").lower():
            # Confronto orario (se presente)
            start_str = e["start"].get("dateTime", e["start"].get("date"))
            if start_str.startswith(date_iso.split("T")[0]): # Controllo base sulla data
                target_event = e
                break
    
    if not target_event:
        return f"Non ho trovato nessun evento chiamato '{summary}' in quella data da cancellare."

    # 2. Eseguiamo l'eliminazione
    try:
        delete_calendar(creds, target_event) #
        return f"Evento '{summary}' eliminato correttamente."
    except Exception as e:
        return f"Errore tecnico durante l'eliminazione: {str(e)}"


def tool_update_event(
    old_summary: str, 
    old_date_iso: Optional[str]=None,
    new_summary: Optional[str] = None,     # <--- CAMBIA QUI
    new_start_iso: Optional[str] = None,   # <--- CAMBIA QUI
    new_end_iso: Optional[str] = None      # <--- CAMBIA QUI
):

    """
    Modifica un evento esistente. Cerca l'evento originale e applica i cambiamenti.
    Args:
        old_summary: Titolo attuale dell'evento da modificare.
        old_date_iso: Data attuale dell'evento (per trovarlo).
        new_summary: (Opzionale) Nuovo titolo.
        new_start_iso: (Opzionale) Nuova data inizio ISO.
        new_end_iso: (Opzionale) Nuova data fine ISO.
    """
    creds = accesso()
    
    # 1. Troviamo l'evento vecchio
    try:
        target_date = datetime.datetime.fromisoformat(old_date_iso)
    except ValueError:
        return "Errore formato data ricerca."

    date_info = {
        "start": target_date.date().isoformat(),
        "end": target_date.date().isoformat()
    }
    events = read_calendar(creds, date_info)
    
    old_event_obj = None
    for e in events:
        if old_summary.lower() in e.get("summary", "").lower():
             old_event_obj = e
             break
             
    if not old_event_obj:
        return f"Non ho trovato l'evento '{old_summary}' da modificare."

    # 2. Costruiamo il nuovo oggetto evento
    # Se un campo non viene passato, manteniamo quello vecchio
    new_event_dict = {
        "summary": new_summary if new_summary else old_event_obj.get("summary"),
        "description": old_event_obj.get("description", ""),
        "location": old_event_obj.get("location", ""),
    }

    # Gestione date (se cambiano)
    if new_start_iso and new_end_iso:
        new_event_dict["start"] = {"dateTime": new_start_iso, "timeZone": "Europe/Rome"}
        new_event_dict["end"] = {"dateTime": new_end_iso, "timeZone": "Europe/Rome"}
    else:
        # Manteniamo date vecchie
        new_event_dict["start"] = old_event_obj.get("start")
        new_event_dict["end"] = old_event_obj.get("end")

    # 3. Chiamiamo l'update
    try:
        # Nota: update_calendar in calendarapi.py si aspetta (creds, old_event, new_event)
        # Assicurati che new_event sia un dizionario compatibile con parser.format_event
        update_calendar(creds, old_event_obj, new_event_dict) #
        return "Evento aggiornato con successo."
    except Exception as e:
        return f"Errore aggiornamento: {str(e)}"