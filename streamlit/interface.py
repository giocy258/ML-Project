from pathlib import Path
import sys

# Path del file attuale
HERE = Path(__file__).resolve()

# ROOT del progetto → cartella superiore alla cartella "streamlit"
ROOT_DIR = HERE.parent.parent

# aggiungi al Pythonpath
sys.path.insert(0, str(ROOT_DIR))

import json
import pandas as pd
import streamlit as st
from streamlit_calendar import calendar
from cal_config import calendar_options, custom_css
from calendar_agent.agent import root_agent

USER_AVATAR = '🍌'
BOT_AVATAR = '🗓️'
OLLAMA_MODEL = 'llama3:8b-instruct-q5_1'

pd.read_json(r'.\streamlit\cal_events.json')
st.set_page_config(page_title="Calendario", page_icon="🍌", layout="wide")

# Imposta modello di default (Ollama)
if "ollama_model" not in st.session_state:
    st.session_state["ollama_model"] = OLLAMA_MODEL



# ============ TITOLO ============
st.markdown("<h1 style='text-align: center;'>Calendario</h1>", unsafe_allow_html=True)



# ============ BOTTONI ============
col1, col2 = st.columns(2)

with col1:
    st.link_button("📧 Gmail", "https://mail.google.com")

with col2:
    st.link_button("📆 Calendar", "https://calendar.google.com")



# ============ CHAT ============
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get('avatar')):
        st.markdown(message["content"])

if prompt:= st.chat_input('Ask me a question'):
    with st.chat_message('user', avatar=USER_AVATAR):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", 'avatar': USER_AVATAR, "content": prompt})

    with st.chat_message('assistant', avatar=BOT_AVATAR):
        response = root_agent.run(prompt, history=st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", 'avatar': BOT_AVATAR, "content": response})



# ============ SLIDEBAR ============
with open('streamlit/cal_events.json', 'r', encoding='utf-8') as f:
    cal_events = json.load(f)
#print(type(cal_events), cal_events)

with st.sidebar:
    calendar = calendar(
        events=cal_events,
        options=calendar_options,
        custom_css=custom_css,
        key='calendar' # Assign a widget key to prevent state loss,
    )
    st.write("_#Se la visualizzazione del calendario esplode, riavviare la pagina_")

#st.write(calendar)