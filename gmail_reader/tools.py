import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- CONFIGURAZIONE ---
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Regole di categorizzazione
REGOLE = {
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


def connetti_gmail():
    """Effettua il login e restituisce il servizio."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def scarica_mappa_etichette(service):
    """Scarica gli ID delle etichette da Gmail."""
    results = service.users().labels().list(userId='me').execute()
    mappa = {}
    for label in results.get('labels', []):
        nome = label['name'].upper()
        if nome in REGOLE:
            mappa[nome] = label['id']
    return mappa


def analizza_e_categorizza(oggetto, snippet):
    """
    Riceve i dati della mail e decide la categoria.
    Restituisce una stringa (es. 'LAVORO') o None.
    """
    testo_completo = (oggetto + " " + snippet).lower()
    
    # Scorre le regole in ordine
    for categoria, parole_chiave in REGOLE.items():
        for parola in parole_chiave:
            if parola in testo_completo:
                # Decisione presa
                return categoria
    
    return None


def agente_smistatore(service, msg_id, categoria, mappa_etichette):
    """
    Riceve l'ordine di spostamento ed esegue l'azione su Gmail.
    """
    # Verifica sicurezza
    if categoria not in mappa_etichette:
        print(f"   [ERRORE AGENTE] Etichetta '{categoria}' non esiste su Gmail.")
        return False

    label_id = mappa_etichette[categoria]
    
    body = {
        'addLabelIds': [label_id],
        'removeLabelIds': ['INBOX']
    }
    
    try:
        service.users().messages().modify(
            userId='me', 
            id=msg_id, 
            body=body
        ).execute()
        print(f"   [AGENTE] Spostato in -> {categoria}")
        return True
    except HttpError as e:
        print(f"   [AGENTE] Errore tecnico: {e}")
        return False



def main():
    service = connetti_gmail()
    
    # Preparazione strumenti
    mappa_etichette = scarica_mappa_etichette(service)
    
    # Recupero posta
    risultati = service.users().messages().list(userId='me', q='is:unread in:inbox').execute()
    messaggi = risultati.get('messages', [])
    
    if not messaggi:
        print("Nessuna mail da lavorare.")
        return

    print(f"Trovate {len(messaggi)} mail in attesa.")

    for messaggio_ref in messaggi:
        try:
            
            messaggio_id = messaggio_ref['id']
            dettaglio = service.users().messages().get(userId='me', id=messaggio_id).execute()
            
            oggetto = ""
            for h in dettaglio['payload']['headers']:
                if h['name'] == 'Subject':
                    oggetto = h['value']
                    break
            snippet = dettaglio.get('snippet', '')
            
            print(f"Analisi: {oggetto[:30]}...")

            
            decisione_categoria = analizza_e_categorizza(oggetto, snippet)

        
            if decisione_categoria:
                agente_smistatore(service, messaggio_id, decisione_categoria, mappa_etichette)
            else:
                print("   [NESSUNA AZIONE] Categoria non trovata.")

        except Exception as e:
            print(f"Errore imprevisto: {e}")

if __name__ == '__main__':
    main()