import calendarapi
import parser
from datetime import datetime, timedelta
import json

# Importa esplicitamente il tool di consultazione per l'esempio
try:
    from Tools import list_upcoming_events 
except ImportError:
    # Se tools.py non è in un percorso importabile, avvisa e prosegui
    print("ATTENZIONE: Impossibile importare list_upcoming_events da tools.py.")
    print("Assicurati che tools.py sia nella stessa directory o nel PYTHONPATH.")

# Configurazioni per la sincronizzazione automatica

DAYS_TO_SYNC = 30 
START_DATE = datetime.now().strftime('%Y-%m-%d')
END_DATE = (datetime.now() + timedelta(days=DAYS_TO_SYNC)).strftime('%Y-%m-%d')

DATE_INFO = {
    "start": START_DATE,
    "end": END_DATE
}

#funzione di esecuzione

def esegui_sincronizzazione_automatica():
    """
    Esegue l'autenticazione e chiama la funzione di sincronizzazione.
    """
    print("\n[AGENTE BACKEND] Avvio Sincronizzazione...")
    
    try:
        # 1. Autenticazione
        creds = calendarapi.accesso() 
        if not creds:
            print("[ERRORE] Autenticazione fallita.")
            return

        # 2. Esecuzione della Sincronizzazione
        # NOTA: Prima di questa chiamata, i dati sorgente devono popolare 'calendar.json'.
        calendarapi.sync_calendar(creds, DATE_INFO)
        
    except Exception as e:
        print(f"[ERRORE] Sincronizzazione fallita: {e}")

def avvia_consultazione_conversazionale():
    """
    Simula una richiesta utente e la chiamata del tool da parte dell'LLM.
    """
    print("\n[AGENTE CONVERSAZIONALE] Esempio di Consultazione...")
    
    try:
        # 1. Chiamata simulata del tool LLM
        risultato_json = list_upcoming_events(max_results=3)
        
        print("\n[OUTPUT TOOL]")
        print(risultato_json)
        
        # 2. Interpretazione e Risposta (Logica LLM)
        if "Errore" in risultato_json or "Nessun evento" in risultato_json:
            risposta = "Non ho trovato eventi imminenti."
        else:
            eventi = json.loads(risultato_json)
            
            # Qui si integrerebbe la logica di analisi (es. Trovare i conflitti)
            
            risposta = "Ecco i tuoi prossimi impegni (Interpretazione dell'LLM):"
            for ev in eventi:
                 risposta += f"\n- {ev['summary']} inizia il {ev['start']}"
                 
        print(f"\n[RISPOSTA FINALE] {risposta}")

    except NameError:
         print("[SALTO] Consultazione saltata per errore di importazione tool.")
    except Exception as e:
        print(f"[ERRORE] Consultazione fallita: {e}")


if __name__ == "__main__":
    
    # Esegue l'agente di sincronizzazione (tipicamente in background o tramite CRON)
    esegui_sincronizzazione_automatica()
    
    print("\n" + "-"*50)
    
    # Esegue l'agente conversazionale (tipicamente in risposta a un input utente)
    avvia_consultazione_conversazionale()