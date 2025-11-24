import datetime

def format_event(event_data: dict) -> dict:
    """
    Formatta un dizionario di dati grezzi in una struttura 'Resource' 
    valida per le API di Google Calendar (v3).
    
    Accetta in input un dizionario che può contenere:
    - summary (str)
    - location (str)
    - description (str)
    - start (str ISO format o dict)
    - end (str ISO format o dict)
    - colorId (str)
    """
    
    # 1. Recupero campi base
    summary = event_data.get('summary', 'Nuovo Evento')
    location = event_data.get('location', '')
    description = event_data.get('description', '')
    
    # 2. Gestione Colori (mapping semplificato)
    # Se viene passato un numero o un ID colore, lo usiamo.
    # Altrimenti default (None lascia il colore predefinito del calendario)
    color_id = event_data.get('colorId')
    
    # 3. Gestione Date (Start e End)
    # Le API di Google vogliono: {'dateTime': 'ISO_STRING', 'timeZone': '...'}
    # Il tuo tools.py potrebbe passare già il dict oppure solo la stringa.
    start_data = _format_date_field(event_data.get('start'))
    end_data = _format_date_field(event_data.get('end'))

    # Costruzione del dizionario finale per le API Google
    google_event_resource = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': start_data,
        'end': end_data,
        'reminders': {
            'useDefault': True  # Meglio usare le impostazioni di default dell'utente
        }
    }

    # Aggiungi colorId solo se presente (altrimenti Google usa il default)
    if color_id:
        google_event_resource['colorId'] = str(color_id)

    return google_event_resource


def _format_date_field(date_value):
    """
    Helper interno per assicurarsi che la data sia nel formato dizionario richiesto da Google.
    """
    if not date_value:
        # Fallback se manca la data (es. usa ora attuale)
        now = datetime.datetime.now().isoformat()
        return {'dateTime': now, 'timeZone': 'Europe/Rome'}

    # Se è già un dizionario (es. creato da tools.py), lo ritorniamo così com'è
    if isinstance(date_value, dict):
        # Assicuriamoci che ci sia la timeZone se è un dateTime
        if 'dateTime' in date_value and 'timeZone' not in date_value:
            date_value['timeZone'] = 'Europe/Rome'
        return date_value

    # Se è una stringa (es. "2023-11-24T15:00:00"), la impacchettiamo
    if isinstance(date_value, str):
        return {
            'dateTime': date_value,
            'timeZone': 'Europe/Rome'
        }
        
    # Se è un oggetto datetime
    if isinstance(date_value, datetime.datetime):
        return {
            'dateTime': date_value.isoformat(),
            'timeZone': 'Europe/Rome'
        }

    return date_value

# Manteniamo la legenda dei colori come riferimento utile (può servire all'LLM in futuro)
AVAILABLE_COLORS = {
    '1': 'Azzurro',
    '2': 'Verde Chiaro',
    '3': 'Lilla',
    '4': 'Rosa',
    '5': 'Giallo',
    '6': 'Arancione',
    '7': 'Turchese',
    '8': 'Grigio',
    '9': 'Blu scuro',
    '10': 'Verde',
    '11': 'Rosso'
}