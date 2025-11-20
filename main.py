# main.py
import os
import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Importiamo i tools definiti prima
from Tools import (
    tool_list_upcoming_events, 
    tool_safe_add_event, 
    tool_force_add_event, 
    tool_find_availability
)

# Carica la API KEY (assicurati di averla nel file .env o nelle variabili d'ambiente)
load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# --- CONFIGURAZIONE TOOLS ---
# Lista delle funzioni che l'agente può "vedere" e chiamare
my_tools = [
    tool_list_upcoming_events, 
    tool_safe_add_event, 
    tool_force_add_event, 
    tool_find_availability
]

# --- SYSTEM PROMPT (IL CERVELLO) ---
def get_system_instruction():
    now = datetime.datetime.now()
    # Formattiamo la data chiaramente per l'LLM
    today_str = now.strftime("%A, %d %B %Y, ore %H:%M")
    
    return f"""
    Sei un assistente personale intelligente per la gestione del calendario.
    
    DATI CONTESTUALI:
    - Oggi è: {today_str}
    - Fuso orario: Europe/Rome
    
    LE TUE REGOLE OPERATIVE:
    1. GESTIONE DATE:
       - Quando l'utente dice "domani" o "lunedì prossimo", calcola la data precisa basandoti su "Oggi è" {today_str}.
       - Nelle chiamate ai tool, usa SEMPRE il formato ISO-8601: YYYY-MM-DDTHH:MM:SS (es: 2025-11-21T15:30:00).
    
    2. AGGIUNTA EVENTI (LOGICA DI SICUREZZA):
       - Se l'utente chiede di aggiungere un evento, usa PRIMA 'tool_safe_add_event'.
       - Se 'tool_safe_add_event' restituisce che lo slot è occupato e suggerisce un'alternativa, comunicala all'utente e chiedi conferma prima di riprovare.
       - Usa 'tool_force_add_event' SOLO se l'utente dice esplicitamente frasi come "non importa", "sovrascrivi", "segnalo lo stesso".
    
    3. RICERCA SPAZI:
       - Se l'utente è vago (es: "trovami un'ora per studiare"), usa 'tool_find_availability'.
    
    4. STILE DI RISPOSTA:
       - Sii conciso. Conferma sempre l'avvenuta creazione dell'evento con orario e titolo.
       - Se c'è un errore tecnico, spiegalo semplicemente.
    """

# --- INIZIALIZZAZIONE MODELLO ---
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash', # O 'gemini-1.5-pro' per più intelligenza
    tools=my_tools,
    system_instruction=get_system_instruction()
)

# Avvia la chat con la gestione automatica delle chiamate alle funzioni
chat = model.start_chat(enable_automatic_function_calling=True)

def main():
    print("🤖 Agente Calendar avviato! (Scrivi 'exit' per uscire)")
    print(f"📅 Data rilevata sistema: {datetime.datetime.now().strftime('%d/%m/%Y')}")
    
    while True:
        user_input = input("\nTu: ")
        if user_input.lower() in ["exit", "esci", "quit"]:
            break
            
        try:
            # Invia il messaggio. Grazie a enable_automatic_function_calling, 
            # se il modello decide di usare un tool, lo esegue e si gestisce la risposta da solo.
            response = chat.send_message(user_input)
            print(f"Agente: {response.text}")
            
        except Exception as e:
            print(f"⚠️ Errore: {e}")

if __name__ == "__main__":
    main()