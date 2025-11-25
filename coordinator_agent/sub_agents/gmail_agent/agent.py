from google.adk.agents import LlmAgent
import os
from dotenv import load_dotenv

# --- IMPORT RELATIVI ---
from .utils import load_markdown_content
from .tools import (
    tool_datetime_now,
    tool_search_gmail,
    tool_find_contacts,
    tool_send_email_message,
    tool_manage_email
)

# --- PERCORSI ASSOLUTI DINAMICI ---
# 1. Percorso assoluto della cartella
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Percorsi per i prompt collegandoli a BASE_DIR
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
DESCRIPTION_PATH = os.path.join(PROMPTS_DIR, "description.md")
INSTRUCTION_PATH = os.path.join(PROMPTS_DIR, "instruction.md")

# 3. Percorso per il .env (che sta un livello sopra, nella root)
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
    tool_datetime_now,
    tool_search_gmail,
    tool_find_contacts,
    tool_send_email_message,
    tool_manage_email
    ],
    sub_agents=[]
)