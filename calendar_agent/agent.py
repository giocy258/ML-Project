from google.adk.agents import LlmAgent
import os
from dotenv import load_dotenv

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

# 1) Ottieni il percorso assoluto della cartella dove si trova QUESTO file (agent.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2) Costruisci i percorsi per i prompt collegandoli a BASE_DIR
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
DESCRIPTION_PATH = os.path.join(PROMPTS_DIR, "description.md")
INSTRUCTION_PATH = os.path.join(PROMPTS_DIR, "instruction.md")

#3) il percorso per il .env (che sta un livello sopra, nella root)
DOTENV_PATH = os.path.join(BASE_DIR, "..", ".env")

# Carica le variabili d'ambiente
load_dotenv(dotenv_path=DOTENV_PATH)

FLASH_MODEL = "gemini-2.5-flash"
PRO_MODEL = "gemini-2.5-pro"

# andiamo a definire l'agente
calendaragent = LlmAgent(
    name="CalendarManagementAgent",
    description=load_markdown_content(DESCRIPTION_PATH),
    instruction=load_markdown_content(INSTRUCTION_PATH),
    model=FLASH_MODEL,
    tools=[
        tool_find_availability,
        tool_list_upcoming_events,
        tool_force_add_event,
        tool_safe_add_event,
        tool_delete_event,
        tool_update_event,
        tool_datetime_now
    ],
    sub_agents=[]
)