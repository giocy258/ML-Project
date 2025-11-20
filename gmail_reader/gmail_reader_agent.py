import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Funzione per caricare le istruzioni
def load_prompt(file_path):
    with open(file_path, 'r') as f:
        return f.read()

# Funzione per interagire con l'LLM (simulata qui)
def categorize_with_llm(instruction, email_content):
    # QUI inseriresti la logica per chiamare l'API di un LLM (OpenAI, Gemini, Anthropic, ecc.)
    # Inviando sia l'istruzione (instruction) che il contenuto dell'email (email_content)
    # e recuperando la categoria.
    print(f"Richiesta all'LLM per l'email: {email_content[:50]}...")
    # --- Simulazione ---
    if "scadenza" in email_content.lower() or "cliente" in email_content.lower():
        return "Lavoro"
    elif "netflix" in email_content.lower() or "amici" in email_content.lower():
        return "Vita privata"
    elif "urgente" in email_content.lower():
        return "Urgenti"
    return "Vita privata" # Categoria di default
    # -------------------

# Logica principale
def run_agent():
    # 1. Carica le istruzioni
    instruction_prompt = load_prompt(r"gmail_reader\prompts\instruction.md")

    # 2. Autenticazione (Utilizzare la libreria ufficiale di Google per l'API di Gmail)
    # SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    # flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    # creds = flow.run_local_server(port=0)
    # service = build('gmail', 'v1', credentials=creds)
    # results = service.users().messages().list(userId='me', maxResults=5).execute()
    
    # 3. Iterazione e Categorizzazione (Simulazione)
    email_list = [
        {"subject": "Riunione di progetto Lunedì", "body": "Non dimenticare la scadenza di Lunedì prossimo."},
        {"subject": "Sconti Netflix", "body": "Ciao! Ho trovato un film da vedere con gli amici."},
        {"subject": "AZIONE URGENTE: Server Critico", "body": "Il server è in stato critico e richiede un intervento urgente!"}
    ]

    print("\n--- Analisi Email ---")
    for email in email_list:
        content = f"Oggetto: {email['subject']}\nCorpo: {email['body']}"
        categoria = categorize_with_llm(instruction_prompt, content)
        print(f"📧 Oggetto: {email['subject']} -> Categoria: **{categoria}**")

if __name__ == '__main__':
    run_agent()