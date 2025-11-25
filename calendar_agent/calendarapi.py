# api google calendar qui
# richiesto tzdata per il database dei fusi orari
import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError # pip install tzdata
import os.path
import os
from . import my_parser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def accesso() -> Credentials:
    """
    Gestisce l'autenticazione cercando i file json NELLA STESSA CARTELLA di questo script.
    """
    import os # Assicuriamoci che os sia importato
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    
    
    # 1) Trova la cartella dove si trova fisicamente QUESTO file (calendarapi.py)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2) Costruisce i percorsi completi ("C:/.../calendar/token.json")
    token_path = os.path.join(base_dir, "token.json")
    creds_path = os.path.join(base_dir, "credentials.json")
    
    # Usa token_path invece di "token.json"
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # CONTROLLO DI SICUREZZA
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"CRITICO: Non trovo il file credentials.json qui: {creds_path}")
                
            # Usa creds_path invece di "credentials.json"
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
            
        # Salva il token nel percorso corretto
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

def read_calendar(creds: Credentials, date_info: dict) -> list: 
    """
    Legge gli eventi da Google Calendar per un intervallo di date specificato, 
    escludendo i weekend e filtrando solo gli eventi il cui summary inizia con "UFS" o "UFT".
    Update: deve leggere eventi "PW" e "Extra Orario".

    Args:
        creds (Credentials): Credenziali per accedere all'API di Google Calendar.
        date_info (dict): Dizionario contenente le date di inizio "start" e fine "end" in formato YYYY-MM-DD 
                          che definiscono l'intervallo di ricerca degli eventi.

    Returns:
        list: Lista di eventi (sotto forma di dizionari) che soddisfano il filtro richiesto.
    """
    # gestisco i fusi orari in modo corretto
    try:
        local_tz = ZoneInfo("Europe/Rome")
    except ZoneInfoNotFoundError:
        print(f"Fuso orario non trovato. Assicurati che il database tzdata sia installato e accessibile ('pip install tzdata')")
        # exit("Impossibile determinare il fuso orario")

    try:
        service = build("calendar", "v3", credentials=creds)
        all_events = []

        # estrai le date di inizio e fine
        start_date = datetime.datetime.fromisoformat(date_info["start"])
        end_date = datetime.datetime.fromisoformat(date_info["end"])

        current_date = start_date

        # itera attraverso ogni giorno nell'intervallo
        while current_date <= end_date:

            # definisci l'intervallo di tempo per il giorno corrente
            start_of_day_local = datetime.datetime(current_date.year, current_date.month, current_date.day, 00, 00, 0, tzinfo=local_tz)
            end_of_day_local = datetime.datetime(current_date.year, current_date.month, current_date.day, 23, 59, 0, tzinfo=local_tz)

            # converti in UTC usando il metodo standard astimezone
            start_of_day_utc = start_of_day_local.astimezone(datetime.timezone.utc).isoformat()
            end_of_day_utc = end_of_day_local.astimezone(datetime.timezone.utc).isoformat()

            # i print finiscono nei log
            # gli orari sono corretti, interroga l'api in UTC
            print(f"Recupero eventi dal {start_of_day_utc} al {end_of_day_utc}")

            # ottiene gli eventi da Calendar
            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=start_of_day_utc,
                    timeMax=end_of_day_utc,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            if events:
                all_events.extend(events)
           # incrementa la data per il giorno successivo
            current_date += datetime.timedelta(days=1)

        if not all_events:
            print("Nessun evento trovato nell'intervallo di date specificato.")  
            return []

        for event in all_events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

        return all_events

    except HttpError as error:
        print(f"Si è verificato un errore durante la lettura: {error}")


def add_calendar(creds: Credentials, event: dict): # aggiunge singolarmente perché gestisco i loop meglio se ci sono condizioni
    """
    Aggiunge un singolo evento a Google Calendar.

    Args:
        creds (Credentials): Credenziali per l'accesso all'API di Google Calendar.
        event (dict): Dizionario contenente i dati dell'evento da aggiungere.\n 
                    Il dizionario verrà formattato tramite `parser.format_event`.
    """

    try:
        service = build("calendar", "v3", credentials=creds)

        event = my_parser.format_event(event)
        evento = service.events().insert(calendarId = "primary", body = event).execute()

        print(f"Evento creato: {evento.get("htmlLink")}")

    except HttpError as error:
        print(f"Errore durante il caricamento dell'evento: {error}")


def delete_calendar(creds: Credentials, event): # rimuove singolarmente
    """
    Elimina un singolo evento da Google Calendar.

    Args:
        creds (Credentials): Credenziali per l'accesso all'API di Google Calendar.
        event (dict): Dizionario contenente i dettagli dell'evento da eliminare, 
                    incluso l'ID dell'evento.
    """
    try:
        service = build("calendar", "v3", credentials=creds)

        evento = event.get('id')
        service.events().delete(calendarId='primary', eventId=evento).execute()

        print(f"Evento eliminato dal calendario: {event.get('summary', 'Senza titolo')} - {event['start'].get('dateTime', event['start'].get('date'))}")

    except HttpError as error:
        print(f"Errore durante l'eliminazione dell'evento '{event.get('summary', 'Senza titolo')}': {error}")


def update_calendar(creds: Credentials, old_event: dict, new_event: dict): # aggiorna singolarmente
    """
    Aggiorna un evento esistente nel calendario Google Calendar.

    Args:
        creds (Credentials): Credenziali per accedere all'API di Google Calendar.
        old_event (dict): Dizionario contenente i dettagli dell'evento da aggiornare, incluso l'ID dell'evento.
        new_event (dict): Dizionario contenente i nuovi dati dell'evento che verrà utilizzato per l'aggiornamento.\n
                        Il dizionario verrà formattato tramite `parser.format_event`.
    """
    try:
        service = build("calendar", "v3", credentials=creds)

        event_id = old_event.get('id')
        new_event = my_parser.format_event(new_event)

        service.events().update(calendarId='primary', eventId=event_id, body=new_event).execute()

        print(f"Evento aggiorato dal calendario: {old_event.get('summary', 'Senza titolo')} - {old_event['start'].get('dateTime', old_event['start'].get('date'))}")

    except HttpError as error:
        print(f"Errore durante l'aggiornamento dell'evento '{old_event.get('summary', 'Senza titolo')}': {error}")


def get_available_colors(creds):
    try:
        service = build("calendar", "v3", credentials=creds)
        colors = service.colors().get().execute()
        print(colors['event'])
        return colors['event']
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None