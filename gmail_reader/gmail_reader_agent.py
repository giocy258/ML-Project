from google.adk.agents import LlmAgent
import os
from dotenv import load_dotenv

# --- IMPORT RELATIVI CORRETTI ---
# Nota il punto . davanti
from .utils import load_markdown_content
from .tools import (
    tool_find_availability,
    tool_list_upcoming_events,
    tool_force_add_event,
    tool_safe_add_event,
    tool_delete_event,
    tool_update_event,
    tool_datetime_now
)

# --- MAGIA DEI PERCORSI (LA SOLUZIONE) ---
# 1. Ottieni il percorso assoluto della cartella dove si trova QUESTO file (agent.py)
#    Indipendentemente da dove lanci il comando 'adk', questo sarà sempre corretto.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Costruisci i percorsi per i prompt collegandoli a BASE_DIR
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
DESCRIPTION_PATH = os.path.join(PROMPTS_DIR, "description.md")
INSTRUCTION_PATH = os.path.join(PROMPTS_DIR, "instruction.md")

# 3. Costruisci il percorso per il .env (che sta un livello sopra, nella root)
DOTENV_PATH = os.path.join(BASE_DIR, "..", ".env")

# Carica le variabili d'ambiente
load_dotenv(dotenv_path=DOTENV_PATH)

FLASH_MODEL = "gemini-2.5-flash"
PRO_MODEL = "gemini-2.5-pro"

# --- DEFINIZIONE AGENTE ---
gmail_reader_agent = LlmAgent(
    name="gmail_reader_agent",
    # Ora passiamo i percorsi calcolati, non stringhe fisse
    description=load_markdown_content(DESCRIPTION_PATH),
    instruction=load_markdown_content(INSTRUCTION_PATH),
    model=FLASH_MODEL,
    tools=[
    ],
    sub_agents=[]
)

<<<<<<< Updated upstream
    gmail_reader_agent = LlmAgent(
        name="gmail_reader_agent",
        description=load_description(file_path=PROMPT_FOLDER / "description.md"),
        instruction=load_instruction(file_path=PROMPT_FOLDER / "instruction.md"),
        model="gemini-2.5-flash-lite",
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
=======
root_agent = gmail_reader_agent
>>>>>>> Stashed changes
