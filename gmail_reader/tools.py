import datetime
import re
from zoneinfo import ZoneInfo
from typing import Optional, List
from .gmailapi import accesso, read_emails, send_email, trash_email, update_email_labels

def tool_datetime_now(tz_name: str = "Europe/Rome") -> datetime.datetime:
    """
    Restituisce la data e l'ora attuali localizzate.
    """
    local_tz = ZoneInfo(tz_name)
    return datetime.datetime.now(local_tz)

def tool_search_gmail(query: str, limit: int = 5) -> str:
    """
    [PRINCIPALE] Cerca e legge le email usando la sintassi di ricerca Gmail.
    
    Args:
        query (str): La query di ricerca. Esempi:
                     - "is:unread" -> Legge le nuove email non lette.
                     - "from:amazon" -> Cerca email da Amazon.
                     - "subject:fattura" -> Cerca email con 'fattura' nell'oggetto.
                     - "is:unread from:Giovanni" -> Cerca le non lette di Giovanni.
        limit (int): Numero max di risultati (default 5).
    """
    creds = accesso()
    emails = read_emails(creds, query=query, max_results=limit)
    
    if not emails:
        return f"Nessuna email trovata per la query: '{query}'."
        
    output = []
    output.append(f"Risultati per '{query}':\n")
    
    for email in emails:
        snippet_clean = email['snippet'].replace('\n', ' ').strip()
        # Formattazione compatta ma ricca di info
        output.append(f"- ID: {email['id']} | [{email['date']}]\n  Da: {email['sender']}\n  Oggetto: {email['subject']}\n  Anteprima: {snippet_clean}...")
    
    return "\n---\n".join(output)

def tool_find_contacts(name: str) -> str:
    """
    Cerca indirizzi email validi nello storico messaggi basandosi su un nome.
    Da usare SEMPRE prima di inviare un'email se non si ha l'indirizzo esatto.
    """
    creds = accesso()
    query = f"from:{name}"
    
    # Cerchiamo su un campione più ampio per trovare l'indirizzo giusto
    emails = read_emails(creds, query=query, max_results=15)
    
    if not emails:
        return f"Non ho trovato nessun indirizzo email storico associato al nome '{name}'."

    unique_contacts = set()

    for email in emails:
        raw_sender = email['sender']
        # Estrae l'indirizzo email pulito tra < >
        match = re.search(r'<([^>]+)>', raw_sender)
        
        email_address = ""
        display_name = raw_sender
        
        if match:
            email_address = match.group(1)
            display_name = raw_sender.replace(f"<{email_address}>", "").strip().replace('"', '')
        else:
            email_address = raw_sender
            display_name = "N/A"

        # Aggiunge al set per evitare duplicati
        if email_address and '@' in email_address:
             if email_address not in [x[1] for x in unique_contacts]:
                unique_contacts.add((display_name, email_address))

    if not unique_contacts:
         return f"Ho trovato email da '{name}', ma non sono riuscito a isolare un indirizzo."

    output_str = f"Contatti trovati per '{name}':\n"
    for name, email in unique_contacts:
        output_str += f"- {name}: {email}\n"
        
    return output_str

def tool_send_email_message(recipient: str, subject: str, text_body: str) -> str:
    """
    Invia un'email. Richiede l'indirizzo email esatto del destinatario.
    """
    creds = accesso()
    res = send_email(creds, recipient, subject, text_body)
    
    if res:
        return f"Email inviata a {recipient}. ID: {res['id']}"
    return "Errore invio email."

def tool_manage_email(msg_id: str, action: str) -> str:
    """
    Gestisce lo stato di un'email (segna come letta o cestina).
    
    Args:
        msg_id (str): L'ID del messaggio.
        action (str): L'azione da eseguire. Può essere solo 'mark_read' o 'trash'.
    """
    creds = accesso()
    
    if action == 'mark_read':
        update_email_labels(creds, msg_id, remove_labels=['UNREAD'])
        return f"Messaggio {msg_id} segnato come letto."
    
    elif action == 'trash':
        try:
            trash_email(creds, msg_id)
            return f"Messaggio {msg_id} spostato nel cestino."
        except Exception as e:
            return f"Errore cestinamento: {e}"
            
    else:
        return "Azione non valida. Usa 'mark_read' o 'trash'."