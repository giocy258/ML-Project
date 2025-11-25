import datetime
from zoneinfo import ZoneInfo
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def trova_slot_alternativo(creds: Credentials, duration_minutes: int, start_search_from: datetime.datetime = None, search_days: int = 3, buffer_minutes: int = 30) -> str:
    """
    Trova il primo slot libero disponibile.
    Gestisce correttamente la conversione delle stringhe ISO di Google in oggetti datetime.
    """
    # 1. Definiamo la Timezone subito per evitare errori
    local_tz = ZoneInfo("Europe/Rome")
    
    # 2. Setup data di partenza
    if start_search_from:
        now_local = start_search_from
        # Assicuriamoci che abbia la timezone
        if now_local.tzinfo is None:
            now_local = now_local.replace(tzinfo=local_tz)
    else:
        now_local = datetime.datetime.now(local_tz)

    try:
        service = build("calendar", "v3", credentials=creds)
        
        current_search_time = now_local
        # Arrotondiamo ai prossimi 15 minuti per pulizia
        minutes = (current_search_time.minute // 15 + 1) * 15
        current_search_time = current_search_time.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=minutes)

        days_checked = 0
        
        while days_checked < search_days:
            # Definiamo inizio e fine della giornata lavorativa (o estesa) per la ricerca
            # Qui cerchiamo dalle 08:00 alle 20:00
            day_start_limit = current_search_time.replace(hour=8, minute=0, second=0, microsecond=0)
            day_end_limit = current_search_time.replace(hour=20, minute=0, second=0, microsecond=0)

            # Se siamo già oltre le 20:00, passa a domani
            if current_search_time >= day_end_limit:
                current_search_time = day_start_limit + datetime.timedelta(days=1)
                days_checked += 1
                continue

            # Se siamo prima delle 08:00, porta l'orario alle 08:00
            if current_search_time < day_start_limit:
                current_search_time = day_start_limit

            # Scarichiamo gli eventi del giorno corrente per vedere dove sono i muri
            events_result = service.events().list(
                calendarId='primary',
                timeMin=day_start_limit.isoformat(),
                timeMax=day_end_limit.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            # Iteriamo attraverso gli eventi per saltare gli spazi occupati
            for event in events:
                start_str = event['start'].get('dateTime', event['start'].get('date'))
                end_str = event['end'].get('dateTime', event['end'].get('date'))
                
                try:
                    # fromisoformat gestisce la stringa ISO. 
                    # Se c'è data pura (YYYY-MM-DD), aggiungiamo orario dummy per non crashare
                    if "T" not in start_str: 
                        continue # Ignoriamo eventi tutto il giorno per semplicità in questo slot finder
                        
                    start_busy = datetime.datetime.fromisoformat(start_str)
                    end_busy = datetime.datetime.fromisoformat(end_str)
                except ValueError:
                    continue # Se la data è strana, saltiamo l'evento
                
                # Aggiungiamo il buffer, per esempio 30 min di pausa tra un evento e l'altro
                start_busy = start_busy - datetime.timedelta(minutes=buffer_minutes)
                end_busy = end_busy + datetime.timedelta(minutes=buffer_minutes)

                # CONTROLLO SOVRAPPOSIZIONE
                # Se il nostro cursore è PRONTO, ma c'è un evento che lo blocca:
                # Calcoliamo quando finisce quell'evento e spostiamo il cursore lì.
                
                # Slot richiesto: da current a current + duration
                slot_end = current_search_time + datetime.timedelta(minutes=duration_minutes)
                
                # Logica intersezione: (StartA < EndB) e (EndA > StartB)
                if (current_search_time < end_busy) and (slot_end > start_busy):
                    # C'è conflitto. Spostiamo il cursore alla fine dell'evento + buffer
                    current_search_time = end_busy
                    # Ricalcoliamo i minuti per allinearci
                    if current_search_time.second > 0:
                         current_search_time = current_search_time + datetime.timedelta(minutes=1)
                    current_search_time = current_search_time.replace(second=0, microsecond=0)

            # Dopo aver controllato tutti gli eventi del giorno verifichiamo se lo slot (che ora è libero da conflitti) sta dentro il limite delle 20:00
            final_slot_end = current_search_time + datetime.timedelta(minutes=duration_minutes)
            
            if final_slot_end <= day_end_limit:
                # TROVATO!
                formatted_time = current_search_time.strftime('%A %d/%m alle %H:%M')
                return f" Slot trovato: {formatted_time} (Durata: {duration_minutes} min)"
            
            # Se siamo arrivati a sera senza trovare spazio, passiamo a domani
            current_search_time = day_start_limit + datetime.timedelta(days=1)
            days_checked += 1

        return "Nessuno slot libero trovato nei prossimi giorni."

    except Exception as e:
        return f"Errore durante la ricerca slot: {str(e)}"