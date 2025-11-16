# Importa i tool di ADK
from google_adk import tool

# Importa le librerie Google per l'API e l'autenticazione
import datetime
import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configurazione dell'Autenticazione ---

# Definisci gli scopi (SCOPES). Inizia solo con readonly.
# Se vuoi anche creare eventi, aggiungi 'https...auth/calendar'
# e cancella token.json per ri-autenticarti.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# I file si trovano nella root del progetto, non dentro /adk
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_calendar_service():
    """
    Funzione helper interna. 
    Gestisce l'autenticazione OAuth 2.0 (flusso desktop)
    e restituisce un oggetto 'service' pronto per l'uso.
    """
    creds = None
    # Il file token.json memorizza l'autorizzazione dell'utente.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
    # Se le credenziali non sono valide o mancano, avvia il flusso di login.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print('Refreshing expired credentials...')
            creds.refresh(Request())
        else:
            print('Avvio del flusso di autenticazione...')
            # Questo aprirà una finestra del browser LA PRIMA VOLTA
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Salva le credenziali per la prossima esecuzione
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print(f'Token salvato in {TOKEN_FILE}')

    # Costruisci e restituisci il servizio
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f'Errore nella costruzione del servizio: {error}')
        return None

# --- Definizione dei Tool per l'Agente ---

@tool
def list_upcoming_events(max_results: int = 10) -> str:
    """
    Recupera i prossimi eventi (fino a 'max_results') dal calendario 
    principale dell'utente. Restituisce gli eventi come stringa JSON.
    """
    print(f"Tool 'list_upcoming_events' chiamato con max_results={max_results}")
    service = get_calendar_service()
    if not service:
        return "Errore: Impossibile autenticarsi con Google Calendar."

    try:
        # Chiama l'API Calendar
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indica l'ora UTC
        
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=now,
            maxResults=max_results, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])

        if not events:
            return "Nessun evento imminente trovato."

        # Formatta l'output per l'LLM
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            formatted_events.append({
                'summary': event['summary'],
                'start': start
            })
        
        # Restituisce una stringa JSON che l'LLM può interpretare
        return json.dumps(formatted_events)

    except HttpError as error:
        return f"Si è verificato un errore API: {error}"

# @tool
# def create_calendar_event(summary: str, start_time: str, end_time: str) -> str:
#     """
#     Crea un nuovo evento sul calendario.
#     Le date devono essere in formato ISO 8601 (es. '2025-11-17T09:00:00+01:00').
#     """
#     # Esercizio: implementa questa funzione!
#     # Ricorda di cambiare SCOPES in '.../auth/calendar' e cancellare token.json
#     pass