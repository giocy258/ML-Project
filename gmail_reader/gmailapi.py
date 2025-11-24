import os.path
import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- CONFIGURAZIONE ---
# Se modifichi questi scope, elimina il file token_gmail.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

def accesso() -> Credentials:
    """
    Gestisce l'autenticazione per GMAIL cercando i file json NELLA STESSA CARTELLA di questo script.
    Basato sulla funzione accesso() di calendarapi.py.
    """
    creds = None
    
    # --- MAGIA DEI PERCORSI ASSOLUTI (Presa dal tuo file originale) ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, "token_gmail.json") # Nome diverso per non sovrascrivere quello del calendario
    creds_path = os.path.join(base_dir, "credentials.json")
    # -----------------------------------

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Errore refresh token: {e}")
                os.remove(token_path) # Rimuove token corrotto
                return accesso() # Riprova
        else:
            # CONTROLLO DI SICUREZZA
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"CRITICO: Non trovo il file credentials.json qui: {creds_path}")
                
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
            
        # Salva il token
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

def read_emails(creds: Credentials, query: str = 'is:unread', max_results: int = 10) -> list:
    """
    Legge le email da Gmail basandosi su una query (simile alla barra di ricerca di Gmail).
    Equivale a read_calendar ma usa query string invece di date_info.

    Args:
        creds: Credenziali Gmail.
        query: Stringa di ricerca (es. "from:mario Rossi", "is:unread", "after:2023/01/01").
        max_results: Numero massimo di email da recuperare.
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        
        print(f"Cercando email con query: '{query}'...")
        
        # 1. Ottiene la lista degli ID dei messaggi
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            print("Nessuna email trovata.")
            return []

        full_messages = []
        
        # 2. Ottiene i dettagli per ogni messaggio trovato
        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            
            # Estrazione semplificata dell'oggetto (Snippet + Headers)
            payload = txt.get('payload', {})
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "Senza Oggetto")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Sconosciuto")
            
            print(f"Email trovata: {subject} da {sender}")
            full_messages.append(txt)

        return full_messages

    except HttpError as error:
        print(f"Si è verificato un errore durante la lettura delle email: {error}")
        return []

def send_email(creds: Credentials, to: str, subject: str, body: str):
    """
    Invia un'email. Sostituisce add_calendar.
    """
    try:
        service = build("gmail", "v1", credentials=creds)

        # Creazione del messaggio MIME
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['From'] = 'me' # 'me' usa l'indirizzo autenticato
        message['Subject'] = subject

        # Codifica base64 richiesta da Gmail API
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }

        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        
        print(f"Email inviata! ID Messaggio: {send_message['id']}")
        return send_message

    except HttpError as error:
        print(f"Errore durante l'invio dell'email: {error}")
        return None

def trash_email(creds: Credentials, msg_id: str):
    """
    Sposta un'email nel cestino. Sostituisce delete_calendar.
    Nota: Gmail preferisce 'trash' a 'delete' (che è definitivo).
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        
        service.users().messages().trash(userId='me', id=msg_id).execute()
        print(f"Email {msg_id} spostata nel cestino.")

    except HttpError as error:
        print(f"Errore durante l'eliminazione dell'email: {error}")

# Esempio di utilizzo (da commentare se importato come modulo)
if __name__ == "__main__":
    credenziali = accesso()
    if credenziali:
        # Lettura: Ultimi 5 messaggi non letti
        read_emails(credenziali, query="is:unread", max_results=5)