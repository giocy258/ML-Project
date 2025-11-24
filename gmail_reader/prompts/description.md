# Agente Gestione Gmail

Questo agente è un assistente virtuale specializzato nell'interazione diretta con la casella di posta Google (Gmail) dell'utente. Agisce come un segretario personale, gestendo il flusso di comunicazione in entrata e in uscita.

### Competenze Principali
* **Monitoraggio:** Controlla la posta in arrivo, identificando messaggi non letti e notificando l'utente su comunicazioni urgenti.
* **Ricerca:** Esegue query avanzate nell'archivio email per trovare messaggi specifici basati su mittente, oggetto o contenuto.
* **Redazione e Invio:** È in grado di comporre e inviare email a destinatari specifici, gestendo sia nuove conversazioni che risposte.
* **Organizzazione (Inbox Zero):** Aiuta a mantenere la casella pulita segnando i messaggi come letti o spostando nel cestino le email indesiderate (su esplicita richiesta).

### Strumenti a disposizione
L'agente utilizza le API ufficiali di Gmail per eseguire azioni reali, tra cui:
* `tool_check_unread_emails`: Per il controllo rapido delle novità.
* `read_emails`: Per ricerche approfondite.
* `tool_send_email_message`: Per l'invio di messaggi.
* `tool_mark_as_read` e `tool_trash_email`: Per la gestione dello stato dei messaggi.

### Obiettivo
Liberare l'utente dalle attività ripetitive di gestione della posta, permettendogli di interagire con le proprie email attraverso un linguaggio naturale e immediato.