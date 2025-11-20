import json
import requests
import streamlit as st
from streamlit_calendar import calendar
from utility import stream_ollama

USER_AVATAR = '😄'
BOT_AVATAR = '👾'
OLLAMA_MODEL = 'llama3:8b-instruct-q5_1'

calendar_options = {
    "editable": True,
    "selectable": True,
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
    },
    "slotMinTime": "06:00:00",
    "slotMaxTime": "18:00:00",
    "initialView": "resourceTimelineDay",
    "resourceGroupField": "building",
    "resources": [
        {"id": "a", "building": "Building A", "title": "Building A"},
        {"id": "b", "building": "Building A", "title": "Building B"},
        {"id": "c", "building": "Building B", "title": "Building C"},
        {"id": "d", "building": "Building B", "title": "Building D"},
        {"id": "e", "building": "Building C", "title": "Building E"},
        {"id": "f", "building": "Building C", "title": "Building F"},
    ],
}
calendar_events = [
    {
        "title": "Event 1",
        "start": "2023-07-31T08:30:00",
        "end": "2023-07-31T10:30:00",
        "resourceId": "a",
    },
    {
        "title": "Event 2",
        "start": "2023-07-31T07:30:00",
        "end": "2023-07-31T10:30:00",
        "resourceId": "b",
    },
    {
        "title": "Event 3",
        "start": "2023-07-31T10:40:00",
        "end": "2023-07-31T12:30:00",
        "resourceId": "a",
    }
]
custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""
calendar = calendar(
    events=calendar_events,
    options=calendar_options,
    custom_css=custom_css,
    key='calendar', # Assign a widget key to prevent state loss
)
st.write(calendar)


with st.sidebar:
    st.divider()
    st.caption('by Slope')
    clear_button = st.sidebar.button('Pulisci la chat')

if clear_button:
    st.session_state.messages = []

# Imposta modello di default (Ollama)
if "ollama_model" not in st.session_state:
    st.session_state["ollama_model"] = OLLAMA_MODEL

st.title('Small chatbot App')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get('avatar')):
        st.markdown(message["content"])

prompt = st.chat_input('Ask me a question')

if prompt:
    with st.chat_message('user', avatar=USER_AVATAR):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", 'avatar': USER_AVATAR, "content": prompt})

    with st.chat_message('assistant', avatar=BOT_AVATAR):
        response = st.write_stream(stream_ollama(prompt, model = OLLAMA_MODEL))

    st.session_state.messages.append({"role": "assistant", 'avatar': BOT_AVATAR, "content": response})