# run_agent.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.adk.runners import Runner  # Il motore che serve per Agent.py
from Agent import calendar_agent       # Importiamo il tuo agente definito

# Configurazione iniziale
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    print("Errore: GOOGLE_API_KEY non trovata nel file .env")
    exit()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def main():
    print("🤖 Calendar Agent (ADK Version) Avviato!")
    print("Scrivi 'exit' per chiudere.")

    # Creiamo il Runner passandogli il tuo agente
    runner = Runner(agent=calendar_agent)

    while True:
        user_input = input("\nTu: ")
        
        if user_input.lower() in ["exit", "esci", "quit"]:
            print("Chiusura agente...")
            break

        try:
            # Il runner gestisce tutto: storia della chat, chiamate ai tool, ecc.
            response = runner.run(user_input)
            
            # In ADK la risposta è un oggetto, estraiamo il testo
            print(f"Agente: {response.text}")
            
        except Exception as e:
            print(f"⚠️ Errore durante l'esecuzione: {e}")

if __name__ == "__main__":
    main()