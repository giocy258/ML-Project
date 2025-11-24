import datetime
from zoneinfo import ZoneInfo
from typing import Optional, List
import re
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
    
def tool_search_emails_from_sender(sender: str, limit: int = 5) -> str:
    """
    Cerca le ultime N email ricevute da uno specifico mittente.
    Usa la sintassi di ricerca Gmail 'from:'.
    
    Args:
        sender (str): Il nome o l'indirizzo email del mittente (es. "Mario", "amazon.com", "mario.rossi@email.it").
        limit (int): Quante email recuperare (default 5).
    """
    creds = accesso()
    
    # Costruiamo la query specifica per Gmail
    # Se sender contiene spazi, Gmail gestisce comunque bene la ricerca, 
    # ma per indirizzi esatti è meglio senza spazi.
    query_string = f"from:{sender}"
    
    # Riutilizziamo la tua funzione read_emails
    emails = read_emails(creds, query=query_string, max_results=limit)
    
    if not emails:
        return f"Non ho trovato nessuna email recente inviata da '{sender}'."
        
    output = []
    output.append(f"Risultati ricerca per mittente '{sender}':\n")
    
    for email in emails:
        snippet_clean = email['snippet'].replace('\n', ' ').strip()
        # Includo la data che è fondamentale quando si cerca uno storico
        output.append(f"- [{email['date']}] \n  Oggetto: {email['subject']}\n  ID: {email['id']}\n  Anteprima: {snippet_clean}...")
    
    return "\n---\n".join(output)

def tool_find_contacts(name: str) -> str:
    """
    Cerca nella posta i contatti che corrispondono al nome fornito.
    Utile quando l'utente dice 'scrivi a Giovanni' ma non fornisce l'indirizzo email.
    
    Args:
        name (str): Il nome da cercare (es. "Giovanni", "Rossi").
    """
    creds = accesso()
    
    # Cerchiamo email inviate DA questo nome (è il modo più sicuro per trovare l'indirizzo)
    # Esempio query: "from:giovanni"
    query = f"from:{name}"
    
    # Recuperiamo un buon numero di email per avere più possibilità
    emails = read_emails(creds, query=query, max_results=20)
    
    if not emails:
        return f"Non ho trovato nessun indirizzo email storico associato al nome '{name}'."

    unique_contacts = set()
    output_list = []

    for email in emails:
        raw_sender = email['sender']  # Es: "Giovanni Rossi <giovanni.rossi@gmail.com>"
        
        # Regex per trovare l'email tra parentesi angolari <...> oppure l'email semplice
        match = re.search(r'<([^>]+)>', raw_sender)
        
        email_address = ""
        display_name = raw_sender
        
        if match:
            email_address = match.group(1) # es: giovanni.rossi@gmail.com
            # Puliamo il nome visualizzato rimuovendo l'email
            display_name = raw_sender.replace(f"<{email_address}>", "").strip().replace('"', '')
        else:
            # Se non ci sono <>, assumiamo che sia solo l'email
            email_address = raw_sender
            display_name = "N/A"

        # Creiamo una tupla per il set (così rimuove i duplicati automaticamente)
        if email_address not in [x[1] for x in unique_contacts]:
            unique_contacts.add((display_name, email_address))

    # Formattiamo l'output per l'LLM
    if not unique_contacts:
         return f"Ho trovato delle email da '{name}', ma non sono riuscito a estrarre un indirizzo valido."

    output_str = f"Ho trovato i seguenti contatti per '{name}':\n"
    for name, email in unique_contacts:
        output_str += f"- Nome: {name} | Email: {email}\n"
        
    return output_str