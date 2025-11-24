from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.adk.agents import LlmAgent
from pathlib import Path

PROMPT_FOLDER = Path(r"gmail_reader\prompts")

# Funzione per caricare la description
def load_description(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except:
        return """Un assistente esperto nella gestione delle email. Il suo compito è analizzare il testo grezzo di un'email e assegnarle una singola categoria."""

# Funzione per caricare le istruzioni
def load_instruction(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except:
        return """Sei un assistente esperto nella gestione delle email. 
Il tuo compito è analizzare il testo grezzo di un'email e assegnarle una singola categoria tra le seguenti:
1. **URGENTI**: Qualsiasi email che richieda un'azione immediata, che contenga parole chiave come "urgente," "immediato," "scadenza," "critico," o che provenga da un mittente chiave (come il tuo capo o un'emergenza).
2. **LAVORO**: Email relative a progetti, riunioni, colleghi, clienti, o attività professionali.
3. **PERSONALE**: Email personali, newsletter, social network, acquisti, o comunicazioni familiari/amicali.

Rispondi SOLO con il nome della categoria, nient'altro."""


# Funzione per interagire con l'LLM (simulata qui)
def categorize_with_llm(email_content):
    # QUI inseriresti la logica per chiamare l'API di un LLM (OpenAI, Gemini, Anthropic, ecc.)
    # Inviando sia l'istruzione (instruction) che il contenuto dell'email (email_content)
    # e recuperando la categoria.

    print(f"Richiesta all'LLM per l'email: {email_content[:50]}...")

    gmail_reader_agent = LlmAgent(
        name="gmail_reader_agent",
        description=load_description(file_path=PROMPT_FOLDER / "description.md"),
        instruction=load_instruction(file_path=PROMPT_FOLDER / "instruction.md"),
        model="gemini-2.5-flash-lite",,
        tools=[],
    )
    # --- Simulazione ---
    # if "scadenza" in email_content.lower() or "cliente" in email_content.lower():
    #     return "LAVORO"
    # elif "netflix" in email_content.lower() or "amici" in email_content.lower():
    #     return "PERSONALE"
    # elif "urgente" in email_content.lower():
    #     return "URGENTI"
    # return "PERSONALE" # Categoria di default
    # -------------------

    response = gmail_reader_agent(email_content)

    return response

# Logica principale
def run_agent():
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
        categoria = categorize_with_llm(content)
        print(f"📧 Oggetto: {email['subject']} -> Categoria: **{categoria}**")

if __name__ == '__main__':
    run_agent()