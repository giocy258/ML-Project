from typing import Optional, Dict
import datetime
from zoneinfo import ZoneInfo


def tool_datetime_now(tz_name: str = "Europe/Rome") -> datetime.datetime:

    local_tz = ZoneInfo(tz_name)
    return datetime.datetime.now(local_tz)

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- CONFIGURAZIONE ADK ---
CONFIG = {
    "CREDENTIALS_FILE": "credentials.json",
    "TOKEN_FILE": "token.json",
    "SCOPES": ['https://www.googleapis.com/auth/gmail.modify']
}

# --- DEFINIZIONE REGOLE DEL CERVELLO LOCALE ---
# Questo sostituisce OpenAI. Definiamo le keyword per ogni categoria.
KNOWLEDGE_BASE = {
    "URGENTI": [
        "urgente", "scadenza", "immediato", "critico", "errore", 
        "pagamento", "fattura scaduta", "alert", "importante", "subito"
    ],
    "LAVORO": [
        "meeting", "riunione", "progetto", "cliente", "report", 
        "aggiornamento", "collega", "brief", "presentation", "budget", 
        "fattura", "preventivo", "contratto"
    ],
    "PERSONALE": [
        "newsletter", "ordine", "spedizione", "offerta", "sconto", 
        "social", "facebook", "instagram", "linkedin", "auguri", 
        "invito", "prenotazione", "amazon", "tracking"
    ]
}

class ADKAuth:
    """Modulo Autenticazione Google OAuth2."""
    
    @staticmethod
    def authenticate():
        creds = None
        if os.path.exists(CONFIG["TOKEN_FILE"]):
            creds = Credentials.from_authorized_user_file(CONFIG["TOKEN_FILE"], CONFIG["SCOPES"])
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CONFIG["CREDENTIALS_FILE"]):
                    print("[ERRORE] File credentials.json non trovato.")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CONFIG["CREDENTIALS_FILE"], CONFIG["SCOPES"])
                creds = flow.run_local_server(port=0)
            
            with open(CONFIG["TOKEN_FILE"], 'w') as token:
                token.write(creds.to_json())
        
        return creds

class ADKBrain:
    """Motore Logico Locale (Sostituisce OpenAI)."""
    
    def analyze(self, sender, subject, snippet):
        # Normalizzazione del testo (tutto minuscolo per confronto)
        full_text = f"{subject} {snippet}".lower()
        subject_lower = subject.lower()
        
        scores = {
            "URGENTI": 0,
            "LAVORO": 0,
            "PERSONALE": 0
        }

        # Calcolo punteggi
        for category, keywords in KNOWLEDGE_BASE.items():
            for word in keywords:
                # Regola: Se la parola e' nell'oggetto vale 3 punti, nello snippet vale 1 punto
                if word in subject_lower:
                    scores[category] += 3
                elif word in full_text:
                    scores[category] += 1
        
        # Logica di priorita'
        # Se URGENTI ha anche solo 1 punto, vince su tutto (policy di sicurezza)
        if scores["URGENTI"] > 0:
            return "URGENTI"
            
        # Altrimenti vince chi ha il punteggio piu' alto
        best_category = max(scores, key=scores.get)
        
        # Se il punteggio e' 0, non categorizzare
        if scores[best_category] == 0:
            return None
            
        return best_category

class ADKDispatcher:
    """Agente Operativo su Gmail."""
    
    def __init__(self):
        self.creds = ADKAuth.authenticate()
        if self.creds:
            self.service = build('gmail', 'v1', credentials=self.creds)
        else:
            raise Exception("Autenticazione fallita")
        self.brain = ADKBrain()

    def get_label_ids(self):
        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        label_map = {}
        
        target_categories = KNOWLEDGE_BASE.keys()
        
        for label in labels:
            name = label['name'].upper()
            if name in target_categories:
                label_map[name] = label['id']
        
        return label_map

    def extract_header(self, payload, name):
        headers = payload.get("headers", [])
        for h in headers:
            if h["name"] == name:
                return h["value"]
        return ""

    def run(self):
        print("--- AVVIO SISTEMA ADK (LOCAL LOGIC) ---")
        
        label_map = self.get_label_ids()
        missing = [cat for cat in KNOWLEDGE_BASE.keys() if cat not in label_map]
        
        if missing:
            print(f"[ATTENZIONE] Etichette mancanti su Gmail: {missing}")
            print("Creale manualmente e riavvia lo script.")
            return

        print("Recupero email non lette...")
        # Recupera solo ID e snippet per efficienza
        results = self.service.users().messages().list(
            userId='me', 
            q='is:unread in:inbox'
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("Nessuna email da elaborare.")
            return

        print(f"Trovate {len(messages)} email. Elaborazione in corso...")

        for msg_ref in messages:
            try:
                msg = self.service.users().messages().get(
                    userId='me', 
                    id=msg_ref['id']
                ).execute()
                
                payload = msg['payload']
                subject = self.extract_header(payload, 'Subject')
                sender = self.extract_header(payload, 'From')
                snippet = msg.get('snippet', '')
                
                # Chiamata al Brain Locale
                category = self.brain.analyze(sender, subject, snippet)
                
                if category:
                    target_label_id = label_map[category]
                    
                    body = {
                        'addLabelIds': [target_label_id],
                        'removeLabelIds': ['INBOX']
                    }
                    
                    self.service.users().messages().modify(
                        userId='me', 
                        id=msg_ref['id'], 
                        body=body
                    ).execute()
                    
                    print(f"[SPOSTATO] {subject[:40]}... -> {category}")
                else:
                    print(f"[IGNORATO] {subject[:40]}... (Nessuna corrispondenza)")
                    
            except HttpError as error:
                print(f"[ERRORE API] {error}")
            except Exception as e:
                print(f"[ERRORE GENERICO] {e}")

        print("--- TERMINE OPERAZIONI ---")

if __name__ == '__main__':
    try:
        agent = ADKDispatcher()
        agent.run()
    except Exception as e:
        print(f"Errore critico: {e}")

