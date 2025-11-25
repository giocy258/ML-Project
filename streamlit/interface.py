import streamlit as st
from pathlib import Path
import sys
import json
from streamlit_calendar import calendar
from cal_config import calendar_options, custom_css

# ============ INIZIALIZZAZIONE PERCORSI E AGENTE ============

if "paths_initialized" not in st.session_state:
    # Path del file attuale
    HERE = Path(__file__).resolve()
    # ROOT del progetto → cartella superiore alla cartella "streamlit"
    ROOT_DIR = HERE.parent.parent
    # aggiungi al Pythonpath SOLO UNA VOLTA
    sys.path.insert(0, str(ROOT_DIR))
    # Salva il percorso per l'accesso successivo
    st.session_state["ROOT_DIR"] = ROOT_DIR
    st.session_state["paths_initialized"] = True
    print('Root: ', ROOT_DIR)
else:
    ROOT_DIR = st.session_state["ROOT_DIR"]
    
CAL_EVENTS_PATH = ROOT_DIR / 'streamlit' / 'cal_events.json'


if "coordinator_agent" not in st.session_state:
    from coordinator_agent.agent import get_agent
    st.session_state.coordinator_agent = get_agent()
    print('agente importato')


USER_AVATAR = '🍌'
BOT_AVATAR = '🗓️'

# La linea pd.read_json(r'.\streamlit\cal_events.json') è stata rimossa perché non assegnava un valore e poteva causare errori di percorso.

st.set_page_config(page_title="Calendario", page_icon="🍌", layout="wide")



# ============ TITOLO ============
st.markdown("<h1 style='text-align: center;'>Calendario</h1>", unsafe_allow_html=True)



# ============ BOTTONI ============
col1, col2 = st.columns(2)

with col1:
    st.link_button("📧 Gmail", "https://mail.google.com")

with col2:
    st.link_button("📆 Calendar", "https://calendar.google.com")



# ============ CHAT E LOGICA AGENTE ============
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra messaggi esistenti
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get('avatar')):
        st.markdown(message["content"])



agent = st.session_state.coordinator_agent 

if prompt := st.chat_input("Ask me a question"):

    st.session_state.messages.append({
        "role": "user",
        "avatar": USER_AVATAR,
        "content": prompt
    })

    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)



    # ======== ESECUZIONE AGENTE ========

    try:
        print('1')
        result = agent.chat.send_message(prompt)
        print('2')

        while result.requires_action:
            tool_outputs = []

            for action in result.actions:
                output = action.call()
                tool_outputs.append({"id": action.id, "output": output})

            result = agent.chat.complete(tool_outputs)

        response_text = getattr(result, "output_text", getattr(result, "text", ""))

    except Exception as e:
        st.error(f"❌ Errore nella toolchain ADK: {e}")
        response_text = "⚠️ Errore interno eseguendo un tool."


    # aggiungi messaggio dell’assistente

    st.session_state.messages.append({
        "role": "assistant",
        "avatar": BOT_AVATAR,
        "content": response_text
    })

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        st.markdown(response_text)



# ============ SLIDEBAR (CALENDARIO) ============
try:
    with open(CAL_EVENTS_PATH, 'r', encoding='utf-8') as f:
        cal_events = json.load(f)
except FileNotFoundError:
    st.sidebar.error(f"File eventi non trovato: {CAL_EVENTS_PATH}. Creando una lista vuota.")
    cal_events = []
except Exception as e:
    st.sidebar.error(f"Errore durante la lettura del file eventi: {e}")
    cal_events = []


with st.sidebar:
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>Visualizzazione Eventi</h2>", unsafe_allow_html=True)
    
    calendar_output = calendar(
        events=cal_events,
        options=calendar_options,
        custom_css=custom_css,
        key='calendar' # Assign a widget key to prevent state loss
    )
    
    st.markdown("---")
    st.write("_#Se la visualizzazione del calendario esplode, riavviare la pagina_")
    
    # Debug info (optional)
    # st.write("Ultima interazione calendario:")
    # st.write(calendar_output)