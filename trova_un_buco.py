import datetime
from zoneinfo import ZoneInfo
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials


def trova_slot_alternativo(creds: Credentials, duration_minutes: int, start_search_from: datetime.datetime = None, search_days: int = 3, buffer_minutes: int = 30) -> str:
    # ... setup ...
    
    # Se non viene passata una data specifica, usa ADESSO.
    # Se viene passata (es: la data del conflitto), usa QUELLA.
    if start_search_from:
        now_local = start_search_from
    else:
        now_local = datetime.datetime.now(local_tz)
    """
    Trova il primo slot libero disponibile di durata richiesta nei prossimi giorni, 
    mantenendo un buffer di tempo tra gli eventi.

    Args:
        creds (Credentials): Credenziali per l'accesso all'API di Google Calendar.
        duration_minutes (int): Durata minima dello slot richiesto in minuti.
        search_days (int): Quanti giorni futuri cercare (da oggi).
        buffer_minutes (int): Minuti di cuscinetto tra gli eventi (default 30).

    Returns:
        str: Stringa che suggerisce l'orario alternativo trovato, o un messaggio di fallimento.
    """
    try:
        service = build("calendar", "v3", credentials=creds)
        local_tz = ZoneInfo("Europe/Rome")
    except Exception as e:
        return f"Errore di inizializzazione: {e}"

    # 1. Definisci l'intervallo di ricerca (da ora a X giorni)
    now_local = datetime.datetime.now(local_tz)
    time_min = now_local.isoformat()
    time_max = (now_local + datetime.timedelta(days=search_days)).isoformat()
    
    # 2. Ottieni tutti gli eventi esistenti nel periodo di ricerca
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
    except HttpError as error:
        return f"Errore durante la lettura degli eventi per la ricerca slot: {error}"

    # 3. Prepara gli slot occupati con buffer
    # Converte gli orari in oggetti datetime con fuso orario corretto
    busy_slots = []
    
    # Per semplificare l'analisi, convertiamo tutti gli orari occupati in un formato usabile
    for event in events:
        start_str = event['start'].get('dateTime', event['start'].get('date'))
        end_str = event['end'].get('dateTime', event['end'].get('date'))

        if 'T' in start_str: # Ignora gli eventi All Day
            # Analizza la stringa e converti nel fuso orario locale per l'analisi
            start_dt = datetime.datetime.fromisoformat(start_str).astimezone(local_tz)
            end_dt = datetime.datetime.fromisoformat(end_str).astimezone(local_tz)

            # Estendi l'orario occupato con il buffer richiesto
            # NOTA: Qui estendiamo il blocco occupato per includere il buffer
            busy_start = start_dt - datetime.timedelta(minutes=buffer_minutes)
            busy_end = end_dt + datetime.timedelta(minutes=buffer_minutes)
            
            busy_slots.append((busy_start, busy_end))

    # Ordina gli slot occupati per facilitare l'analisi
    busy_slots.sort(key=lambda x: x[0])
    
    # 4. Cerca lo slot libero (Gap Analysis)
    current_search_time = now_local.replace(hour=8, minute=0, second=0, microsecond=0) # Inizia la ricerca dalle 08:00 di oggi
    required_duration = datetime.timedelta(minutes=duration_minutes)
    
    # Se l'ora attuale è dopo l'inizio della giornata, inizia la ricerca dall'ora attuale
    if now_local > current_search_time:
        current_search_time = now_local

    while current_search_time.date() <= time_max.date():
        
        # Salta i weekend (se necessario, come nel tuo file api.py, qui non è esplicitato per semplicità)
        if current_search_time.weekday() >= 5:
            current_search_time = current_search_time.replace(hour=8, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
            continue
            
        # Limite massimo di ricerca per il giorno corrente (es. fino alle 19:00)
        day_end_limit = current_search_time.replace(hour=19, minute=0, second=0, microsecond=0)

        # Trova il primo blocco occupato che inizia dopo l'ora di ricerca corrente
        for start_busy, end_busy in busy_slots:
            if start_busy > current_search_time:
                # C'è uno slot libero tra current_search_time e start_busy
                free_duration = start_busy - current_search_time
                
                if free_duration >= required_duration:
                    # Trovato uno slot libero!
                    return (
                        f"Slot trovato: **{current_search_time.strftime('%A %d/%m alle %H:%M')}** "
                        f"(Durata: {int(free_duration.total_seconds() / 60)} minuti). "
                        f"L'evento successivo inizia alle {start_busy.strftime('%H:%M')} (incluso buffer)."
                    )
                
                # Sposta l'ora di ricerca alla fine del blocco occupato corrente
                current_search_time = end_busy
            
            elif end_busy > current_search_time:
                # La ricerca corrente è interrotta o si sovrappone a un blocco occupato, 
                # quindi la sposta alla fine del blocco occupato
                current_search_time = end_busy

        # Se non si trova nulla fino a fine giornata, passa al giorno successivo alle 08:00
        if current_search_time < day_end_limit:
            # Se la ricerca è finita, ma non ha ancora raggiunto la fine del giorno, 
            # e non ci sono altri eventi, lo slot è libero fino alla fine del limite.
            remaining_duration = day_end_limit - current_search_time
            if remaining_duration >= required_duration:
                return (
                    f"Slot trovato: **{current_search_time.strftime('%A %d/%m alle %H:%M')}** "
                    f"(Durata: {int(remaining_duration.total_seconds() / 60)} minuti). È libero fino alla fine della giornata lavorativa."
                )

        current_search_time = current_search_time.replace(hour=8, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)


    return f"Nessuno slot libero di {duration_minutes} minuti è stato trovato nei prossimi {search_days} giorni."