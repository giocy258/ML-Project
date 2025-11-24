"""
Coordinator Agent che orchestra calendar_agent e gmail_reader come tools
"""
from typing import Dict, List, Any, Optional
import json
import datetime
from zoneinfo import ZoneInfo

# Import da calendar_agent
from calendar_agent.tools import tool_datetime_now
from calendar_agent.calendarapi import accesso, read_calendar, add_calendar, delete_calendar, update_calendar
from calendar_agent.trova_un_buco import trova_slot_alternativo

# Import da gmail_reader
from gmail_reader.tools import (
    connetti_gmail,
    scarica_mappa_etichette,
    analizza_e_categorizza,
    agente_smistatore,
    connect_to_mail,
    clean_subject,
    categorize_emails,
    REGOLE,
    RULES
)


def get_coordinator_tools() -> List[Dict[str, Any]]:
    """
    Restituisce tutti i tools disponibili dal coordinator
    """
    tools = [
        # Tools Gmail
        {
            "name": "connetti_gmail",
            "description": "Connette a Gmail e restituisce il servizio",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "categorizza_email",
            "description": "Analizza e categorizza le email non lette in base alle regole",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "analizza_email",
            "description": "Analizza oggetto e snippet di una email per categorizzarla",
            "input_schema": {
                "type": "object",
                "properties": {
                    "oggetto": {"type": "string", "description": "Oggetto della email"},
                    "snippet": {"type": "string", "description": "Snippet della email"}
                },
                "required": ["oggetto", "snippet"]
            }
        },
        # Tools Calendario
        {
            "name": "leggi_calendario",
            "description": "Legge gli eventi dal calendario",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "aggiungi_evento",
            "description": "Aggiunge un nuovo evento al calendario",
            "input_schema": {
                "type": "object",
                "properties": {
                    "titolo": {"type": "string"},
                    "data_inizio": {"type": "string"},
                    "data_fine": {"type": "string"}
                },
                "required": ["titolo"]
            }
        },
        {
            "name": "elimina_evento",
            "description": "Elimina un evento dal calendario",
            "input_schema": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"}
                },
                "required": ["event_id"]
            }
        },
        {
            "name": "aggiorna_evento",
            "description": "Aggiorna un evento esistente nel calendario",
            "input_schema": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string"},
                    "nuovi_dati": {"type": "object"}
                },
                "required": ["event_id"]
            }
        },
        {
            "name": "trova_slot_libero",
            "description": "Trova uno slot libero alternativo nel calendario",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "ora_corrente",
            "description": "Restituisce la data e ora corrente localizzata",
            "input_schema": {
                "type": "object",
                "properties": {
                    "tz_name": {"type": "string", "description": "Fuso orario (default: Europe/Rome)"}
                },
                "required": []
            }
        }
    ]
    
    return tools