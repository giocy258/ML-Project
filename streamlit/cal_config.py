calendar_options = {
    "editable": True,
    "selectable": True,
    "headerToolbar": {
        "left": "prev",
        "center": "title",
        "right": "next",
    },
    "footerToolbar": {
        "left": "today",
        "right": "dayGridDay,dayGridWeek,dayGridMonth",
    },
    "slotMinTime": "06:00:00",
    "slotMaxTime": "22:00:00",
    "initialView": "dayGridMonth",
}

custom_css = '''
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
'''