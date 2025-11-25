from google.adk.agents import LlmAgent
import os
from dotenv import load_dotenv

# --- IMPORT RELATIVI ---
from .utils import load_markdown_content
from .sub_agents.calendar_agent.agent import calendaragent
from .sub_agents.gmail_agent.agent import gmail_reader_agent

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
coordinator_agent = LlmAgent(
    name="coordinator_agent",
    description=load_markdown_content(DESCRIPTION_PATH),
    instruction=load_markdown_content(INSTRUCTION_PATH),
    model=FLASH_MODEL,
    tools=[],
    sub_agents=[
        gmail_reader_agent,
        calendaragent
        ]
)

root_agent = coordinator_agent

def get_agent():
    return root_agent