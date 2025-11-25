# Agente Coordinatore (Router Principale)

Questo agente serve come **interfaccia utente principale** e come **motore di routing** per il sistema. La sua unica responsabilità è analizzare l'intenzione dell'utente (email, calendario, o altro) e delegare la richiesta all'agente specializzato più appropriato tra i subordinati.

### Ruolo e Scopo:
Il Coordinator Agent non esegue operazioni dirette (non ha strumenti propri) ma garantisce che ogni richiesta venga instradata al modulo corretto (`gmail_reader_agent` o `calendaragent`), massimizzando l'efficienza e l'accuratezza del sistema.

### Competenze Primarie:
* **Analisi dell'Intenzione:** Classificazione rapida delle richieste in base al dominio (Email vs. Calendario).
* **Delegazione (Routing):** Passaggio dell'intero comando al sub-agent designato.
* **Gestione della Conversazione:** Mantiene il contesto iniziale e garantisce che l'utente interagisca sempre con un unico punto centrale.

### Agenti Subordinati:
* `gmail_reader_agent`: Gestione completa della posta elettronica (lettura, invio, eliminazione).
* `calendaragent`: Gestione completa di eventi e appuntamenti (creazione, ricerca, modifica).