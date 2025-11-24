# api google gmail qui
import os.path
import os
import base64
from email.message import EmailMessage
from typing import List, Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- CONFIGURAZIONE ---
# Se modifichi questi scope, elimina il file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

def accesso() -> Credentials:
    """
    Gestisce l'autenticazione per GMAIL cercando i file json NELLA STESSA CARTELLA di questo script.
    """
    creds = None
    
    # --- MAGIA DEI PERCORSI ASSOLUTI ---
    # 1. Trova la cartella dove si trova fisicamente QUESTO file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Costruisce i percorsi completi (token separato per gmail)
    token_path = os.path.join(base_dir, "token.json") 
    creds_path = os.path.join(base_dir, "credentials.json")
    # -----------------------------------

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Errore durante il refresh del token: {e}")
                # Se il token è corrotto, lo rimuoviamo e riproviamo
                if os.path.exists(token_path):
                    os.remove(token_path)
                return accesso() # Ricorsione sicura per riautenticare
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

def read_emails(creds: Credentials, query: str = 'is:unread', max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Legge le email da Gmail basandosi su una query.

    Args:
        creds: Credenziali Gmail.
        query: Stringa di ricerca (es. "from:mario is:unread", "subject:fattura").
        max_results: Numero massimo di email da recuperare.

    Returns:
        List[Dict]: Lista di dizionari con keys: id, threadId, subject, sender, snippet, date.
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        
        print(f"Cercando email con query: '{query}'...")
        
        # 1. Ottiene la lista degli ID dei messaggi (leggero)
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            print("Nessuna email trovata con questa query.")
            return []

        parsed_messages = []
        
        # 2. Ottiene i dettagli (payload) per ogni messaggio trovato
        # Nota: in produzione massiva si userebbe batch_execute, qui ok loop semplice
        for msg in messages:
            # format='metadata' scarica solo header e non tutto il corpo (più veloce)
            txt = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            
            payload = txt.get('payload', {})
            headers = payload.get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(Nessun Oggetto)")
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Sconosciuto")
            date_sent = next((h['value'] for h in headers if h['name'] == 'Date'), "")
            snippet = txt.get('snippet', "")

            email_data = {
                "id": msg['id'],
                "threadId": msg['threadId'],
                "subject": subject,
                "sender": sender,
                "date": date_sent,
                "snippet": snippet
            }
            
            print(f"- Trovata: {subject} | Da: {sender}")
            parsed_messages.append(email_data)

        return parsed_messages

    except HttpError as error:
        print(f"Si è verificato un errore durante la lettura delle email: {error}")
        return []

def send_email(creds: Credentials, to: str, subject: str, body: str) -> Optional[Dict]:
    """
    Invia un'email. Equivale a add_calendar.
    """
    try:
        service = build("gmail", "v1", credentials=creds)

        # Creazione del messaggio MIME
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['From'] = 'me' # Viene sovrascritto da Gmail con l'account autenticato
        message['Subject'] = subject

        # Codifica base64 url-safe richiesta da Gmail API
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }

        sent_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        
        print(f"Email inviata a {to}! ID: {sent_message['id']}")
        return sent_message

    except HttpError as error:
        print(f"Errore durante l'invio dell'email: {error}")
        return None

def trash_email(creds: Credentials, msg_id: str):
    """
    Sposta un'email nel cestino. Equivale a delete_calendar.
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        
        service.users().messages().trash(userId='me', id=msg_id).execute()
        print(f"Email {msg_id} spostata nel cestino.")

    except HttpError as error:
        print(f"Errore durante l'eliminazione dell'email: {error}")

def update_email_labels(creds: Credentials, msg_id: str, add_labels: List[str] = [], remove_labels: List[str] = []):
    """
    Modifica le etichette di un'email. Equivale a update_calendar.
    Utile per segnare come letto (remove_labels=['UNREAD']) o archiviare (remove_labels=['INBOX']).
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        
        body = {
            "addLabelIds": add_labels,
            "removeLabelIds": remove_labels
        }
        
        service.users().messages().modify(userId='me', id=msg_id, body=body).execute()
        print(f"Email {msg_id} aggiornata (Aggiunti: {add_labels}, Rimossi: {remove_labels})")

    except HttpError as error:
        print(f"Errore durante l'aggiornamento etichette: {error}")