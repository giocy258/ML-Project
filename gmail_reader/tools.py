import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- CONFIGURAZIONE COSTANTE ---
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Base di conoscenza (Regole)
KNOWLEDGE_BASE = {
    "URGENTI": [
        "urgente", "scadenza", "immediato", "critico", "errore", 
        "pagamento", "fattura", "alert", "importante", "subito"
    ],
    "LAVORO": [
        "meeting", "riunione", "progetto", "cliente", "report", 
        "aggiornamento", "collega", "brief", "budget", "contratto"
    ],
    "PERSONALE": [
        "newsletter", "ordine", "spedizione", "offerta", "sconto", 
        "social", "facebook", "linkedin", "auguri", "invito", "amazon"
    ]
}

def get_gmail_service():
    """Gestisce l'autenticazione e restituisce l'oggetto service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print("[ERRORE] File credentials.json mancante.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def get_label_map(service):
    """Restituisce un dizionario {NOME_CATEGORIA: ID_ETICHETTA}."""
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    label_map = {}
    
    target_keys = KNOWLEDGE_BASE.keys()
    
    for label in labels:
        name = label['name'].upper()
        if name in target_keys:
            label_map[name] = label['id']
            
    return label_map


def calculate_category(subject, snippet):
    """Analizza il testo e restituisce la categoria vincente."""
    full_text = f"{subject} {snippet}".lower()
    subject_lower = subject.lower()
    
    scores = {key: 0 for key in KNOWLEDGE_BASE}

    for category, keywords in KNOWLEDGE_BASE.items():
        for word in keywords:
            # 3 punti se la parola e' nell'oggetto
            if word in subject_lower:
                scores[category] += 3
            # 1 punto se e' nell'anteprima
            elif word in full_text:
                scores[category] += 1
    
    # Regola di priorita': Urgenti vince sempre se > 0
    if scores["URGENTI"] > 0:
        return "URGENTI"
        
    best_category = max(scores, key=scores.get)
    
    if scores[best_category] == 0:
        return None
        
    return best_category

def extract_header_value(payload, header_name):
    """Estrae un valore specifico dagli header della mail."""
    headers = payload.get("headers", [])
    for h in headers:
        if h["name"] == header_name:
            return h["value"]
    return ""

# --- 3. FUNZIONI OPERATIVE (LE AZIONI) ---

def fetch_unread_messages(service):
    """Scarica la lista dei messaggi non letti."""
    results = service.users().messages().list(
        userId='me', 
        q='is:unread in:inbox'
    ).execute()
    return results.get('messages', [])

def get_message_details(service, msg_id):
    """Scarica i dettagli di una singola mail."""
    return service.users().messages().get(
        userId='me', 
        id=msg_id
    ).execute()

def move_message(service, msg_id, label_id):
    """Sposta la mail applicando la label e rimuovendo INBOX."""
    body_update = {
        'addLabelIds': [label_id],
        'removeLabelIds': ['INBOX']
    }
    try:
        service.users().messages().modify(
            userId='me', 
            id=msg_id, 
            body=body_update
        ).execute()
        return True
    except HttpError:
        return False

def main():
    
    # 1. Connessione
    service = get_gmail_service()
    if not service:
        print("Impossibile connettersi a Gmail.")
        return

    # 2. Mappatura Etichette
    label_map = get_label_map(service)
    missing_labels = [k for k in KNOWLEDGE_BASE if k not in label_map]
    
    if missing_labels:
        print(f"[ATTENZIONE] Etichette mancanti su Gmail: {missing_labels}")
        print("Lo script continuera', ma ignorera' queste categorie.")

    # 3. Recupero messaggi
    messages = fetch_unread_messages(service)
    if not messages:
        print("Nessuna mail non letta trovata.")
        return

    print(f"Trovate {len(messages)} mail da elaborare.")

    # 4. Ciclo di elaborazione
    for msg_ref in messages:
        try:
            msg_id = msg_ref['id']
            msg_data = get_message_details(service, msg_id)
            
            # Estrazione Dati
            payload = msg_data['payload']
            subject = extract_header_value(payload, 'Subject')
            sender = extract_header_value(payload, 'From')
            snippet = msg_data.get('snippet', '') # Testo anteprima
            
            # Analisi Logica
            category = calculate_category(subject, snippet)
            
            print(f"Analisi: {subject[:40]}...")

            # Smistamento
            if category and category in label_map:
                label_id = label_map[category]
                success = move_message(service, msg_id, label_id)
                if success:
                    print(f"   [SPOSTATO] -> {category}")
                else:
                    print(f"   [ERRORE API] Impossibile spostare.")
            else:
                if category:
                    print(f"   [SALTATO] Categoria '{category}' rilevata ma etichetta mancante.")
                else:
                    print(f"   [IGNORATO] Nessuna categoria corrispondente.")
                    
        except Exception as e:
            print(f"   [ERRORE GENERICO] {e}")

    print("--- OPERAZIONI COMPLETATE ---")

if __name__ == '__main__':
    main()