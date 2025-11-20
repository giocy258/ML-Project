resources = [{"id": "geop", "title": "GEOP"}, {"id": "COLLOQUI", "title": "COLLOQUI"}]

calendar_options = {
    "editable": True,
    "selectable": True,
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "resourceTimelineDay,dayGridMonth",
    },
    "slotMinTime": "06:00:00",
    "slotMaxTime": "22:00:00",
    "initialView": "dayGridMonth",
    "resources": resources,
}

calendar_events = [
    {
        "title": "Event 1",
        "start": "2025-11-20T08:30:00",
        "end": "2025-11-20T10:30:00",
        "resourceId": "geop",
    },
    {
        "title": "Event 2",
        "start": "2025-11-20T07:30:00",
        "end": "2025-11-20T10:30:00",
        "resourceId": "COLLOQUI",
    },
    {
        "title": "Event 3",
        "start": "2025-11-20T10:40:00",
        "end": "2025-11-201T12:30:00",
        "resourceId": "geop",
    }
]

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