import datetime
from zoneinfo import ZoneInfo
from typing import Optional, List
# Assicurati che gmailapi.py sia nella stessa directory e il pacchetto sia gestito correttamente
from .gmailapi import accesso, read_emails, send_email, trash_email, update_email_labels

def tool_datetime_now(tz_name: str = "Europe/Rome") -> datetime.datetime:
    """
    Restituisce la data e l'ora attuali localizzate (aware datetime object).
    Utile per dare contesto temporale all'LLM.
    """
    local_tz = ZoneInfo(tz_name)
    return datetime.datetime.now(local_tz)

def tool_check_unread_emails(limit: int = 5) -> str:
    """
    Controlla le ultime N email non lette nella casella di posta.
    Restituisce una stringa formattata con i dettagli essenziali.
    """
    creds = accesso()
    # Esegue la query per le non lette
    emails = read_emails(creds, query='is:unread', max_results=limit)
    
    if not emails:
        return "Non ci sono nuove email non lette."
        
    output = []
    for email in emails:
        # Costruisce una stringa leggibile per l'LLM
        snippet_clean = email['snippet'].replace('\n', ' ').strip()
        output.append(f"- ID: {email['id']}\n  Da: {email['sender']}\n  Oggetto: {email['subject']}\n  Anteprima: {snippet_clean}...")
    
    return "\n---\n".join(output)

def tool_send_email_message(recipient: str, subject: str, text_body: str) -> str:
    """
    Invia un'email a un destinatario specificato.
    Richiede destinatario, oggetto e corpo del testo.
    """
    creds = accesso()
    res = send_email(creds, recipient, subject, text_body)
    
    if res:
        return f"Email inviata con successo a {recipient}. ID Messaggio: {res['id']}"
    return "Errore durante l'invio dell'email."

def tool_mark_as_read(msg_id: str) -> str:
    """
    Segna un'email come letta rimuovendo l'etichetta 'UNREAD'.
    Richiede l'ID del messaggio (ottenibile da tool_check_unread_emails).
    """
    creds = accesso()
    # Rimuovere 'UNREAD' equivale a segnare come letto in Gmail
    update_email_labels(creds, msg_id, remove_labels=['UNREAD'])
    return f"Messaggio {msg_id} segnato come letto con successo."

def tool_trash_email(msg_id: str) -> str:
    """
    Sposta un'email nel cestino.
    Da usare solo su richiesta esplicita dell'utente.
    """
    creds = accesso()
    try:
        trash_email(creds, msg_id)
        return f"Messaggio {msg_id} spostato nel cestino."
    except Exception as e:
        return f"Errore durante l'eliminazione: {e}"