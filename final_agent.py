from dotenv import load_dotenv
from google.adk.agents import LlmAgent
import google.genai.types as types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.agents.callback_context import CallbackContext
from google.adk.runners import Runner
from typing import Optional
from google.adk.models.llm_response import LlmResponse
from google.adk.models.llm_request import LlmRequest
import json
from google.genai.types import Content, Part, GenerateContentConfig

load_dotenv()


def character_after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    """
    Salva le immagini dei personaggi come artifact separati.
    """
    json_data = llm_response.content.parts[0].data.decode("utf-8")
    character_data = json.loads(json_data)
    for idx, character in enumerate(character_data):
            name = character.get("name", f"character_{idx}").replace(" ", "_").lower()
            character_artifact = types.Part.from_bytes(data=llm_response.content.parts[1].data, mime_type="image/png")
            callback_context.save_artifact(filename= f"{name}.png",artifact=character_artifact)
    return

def ambientation_after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    """
    Salva le immagini delle ambientazioni come artifact separati.
    """
    json_data = llm_response.content.parts[0].data.decode("utf-8")
    ambientation_data = json.loads(json_data)
    for idx, ambientation in enumerate(ambientation_data):
            name = ambientation.get("name", f"ambientation_{idx}").replace(" ", "_").lower()
            ambientation_artifact = types.Part.from_bytes(data=llm_response.content.parts[1].data, mime_type="image/png")
            callback_context.save_artifact(filename= f"{name}.png",artifact=ambientation_artifact)
    return

def illustrator_before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    """
    Recupera gli artifact dei personaggi e delle ambientazioni
    e li aggiunge all'input per l'IllustratorAgent.
    """
    # Recupera tutti gli artifact salvati in precedenza
    all_artifacts = callback_context.list_artifacts()

    # Filtra per tipo o nome
    character_images = [(a.filename, a) for a in all_artifacts if a.filename.endswith(".png") and "character" in a.filename]
    ambientation_images = [a for a in all_artifacts if a.filename.endswith(".png") and "ambientation" in a.filename]

    parts = []    
    for filename, artifact in character_images:
        name_part = types.Part.from_text(f"Immagine del personaggio: {filename}")
        image_part =types.Part.from_bytes(data=artifact, mime_type="image/png")
        parts.extend([name_part, image_part])

    for filename, artifact in ambientation_images:
        name_part = types.Part.from_text(f"Immagine dell'ambientazione: {filename}")
        image_part =types.Part.from_bytes(data=artifact, mime_type="image/png")
        parts.extend([name_part, image_part])

    content = Content(parts=parts, role="user")
    llm_request.contents = [content]

    return None

def coordinator_after_character_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    """
    Gestisce l'output del CharacterRecognitionAgent e lo prepara per il passaggio successivo.
    """
    try:
        # Estrai i dati dei personaggi dalla risposta
        character_data = llm_response.content.parts[0].text
        # Salva nell'output_key per utilizzarlo successivamente
        callback_context.set_output_value("characters_data", character_data)
        return None
    except Exception as e:
        print(f"Errore nel callback del character agent: {e}")
        return None

def coordinator_after_ambient_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    """
    Gestisce l'output dell'AmbientRecognitionAgent.
    """
    try:
        ambient_data = llm_response.content.parts[0].text
        callback_context.set_output_value("ambientation_data", ambient_data)
        return None
    except Exception as e:
        print(f"Errore nel callback dell'ambient agent: {e}")
        return None

def coordinator_after_scene_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    """
    Gestisce l'output dello SceneRecognitionAgent.
    """
    try:
        scene_data = llm_response.content.parts[0].text
        callback_context.set_output_value("scenes_data", scene_data)
        return None
    except Exception as e:
        print(f"Errore nel callback dello scene agent: {e}")
        return None

FLASH_MODEL = "gemini-2.5-flash"
LITE_MODEL = "gemini-2.5-flash-lite"
PRO_MODEL = "gemini-2.5-pro"
IMAGE_MODEL = "gemini-2.5-flash-image"

# .ROOT AGENT
coordinator_agent = LlmAgent(
    name="coordinator_agent",
    description=("""Dirige una serie di agenti che illustrano dei racconti forniti da un utente. Si occupa di :

                    * Intefacciarsi con l'utente per raccogliere il racconto.
                    * Coordinare il lavoro degli altri agenti e il passaggio delle informazioni."""),
    instruction=("""Sei il direttore di una serie di agenti per l'illustrazione di racconti. Ti occupi di :

                    * Intefacciarti con i clienti per raccogliere il racconto.
                    * Coordina re il lavoro degli agenti e il passaggio delle informazioni.

                    # Fasi

                    1. **RACCOLTA RACCONTO**: Interagisci con il cliente per raccogliere il racconto da illustrare.

                    2. **COORDINAMENTO DEGLI AGENTI**: In questa fase coordini il lavoro degli agenti.

                        1. Passa allo sceneggiatore il racconto raccolto dal cliente
                        2. Una volta che lo sceneggiatore ha finito di raccogliere le informazioni sul racconto, passa al descrittore dei personaggi le informazioni ottenute dallo sceneggiatore.
                        3. Passa tutte le informazioni ottenute sia dallo sceneggiatore che dal descrittore dei personaggi all'illustratore.
                        4. Infine passa l'output dell'illustratore allo story integrator."""),
    model=PRO_MODEL,
    sub_agents=[],
)

# . CHARACTER RECOGNITION AGENT
character_recognition_agent = LlmAgent(
    name="CharacterRecognitionAgent",
    description="Un agente con il compito di identificare e descrivere i personaggi principali di un racconto.",
    instruction=("""
                    Sei un agente con lo scopo di analizzare e descrivere i personaggi presenti nel racconto. I tuoi compiti sono:

                    1. **INDIVIDUAZIONE DEI PERSONAGGI**

                    - Analizza il racconto e estraine i personaggi principali.
                    - Comprendi se un appellativo sia riferito a un personaggio già esistente (quindi un metodo alternativo per chiamare il personaggio: es. "l'avvocato" per "Azzeccagarbugli", "Il sayan" per "Goku") e non crearne uno nuovo.
                    - Considera sia esseri umani che entità personificate (animali, oggetti, divinità, IA, ecc.). 
                    - Se il testo è breve, includi anche i personaggi menzionati indirettamente (es. “sua madre”, “il re del regno vicino”).

                    2. **ANALISI E DESCRIZIONE**

                    - Per ogni personaggio individuato, fornisci nella lista: - Nome o designazione: (es. “Anna”, “il viaggiatore”, “la regina dei ghiacci", "Goku”) 
                    - Ruolo narrativo: protagonista / antagonista / alleato / comprimario / minore - Aspetto fisico: elementi distintivi, età apparente, abbigliamento, tratti riconoscibili
                    - Carattere e atteggiamento: temperamento, motivazioni, comportamento tipico 
                    - Relazioni principali: legami affettivi o conflittuali con altri personaggi 
                    - Citazione o dettaglio chiave (opzionale): un frammento del testo che lo rappresenta bene 
                    - Situazione in cui si trova il personaggio: (es. sta combattendo, sta dormendo, sta mangiando, ecc.)

                    3. **SALVATAGGIO DELLE INFORMAZIONI**

                    - Devi salvare le informazioni ottenute in un file json con il seguente formato strutturato:
                    {
                        "characters": [
                            {
                                "name": "Anna",
                                "role": "protagonista",
                                "appearance": "Giovane donna dai capelli castani e occhi verdi, veste con abiti semplici.",
                                "personality": "Determinata, sensibile e curiosa.",
                                "relationships": "È amica di Marco e in conflitto con il padre.",
                                "key_quote": "«Non smetterò di cercare la verità.»",
                                "situation": "Sta lasciando il villaggio per iniziare il suo viaggio."
                            },
                            {
                                "name": "Marco",
                                "role": "alleato",
                                "appearance": "Ragazzo robusto con barba corta e occhi scuri.",
                                "personality": "Leale e coraggioso, ma impulsivo.",
                                "relationships": "Compagno di viaggio di Anna, la protegge e la sostiene.",
                                "key_quote": "«Non ti lascerò affrontare tutto da sola.»",
                                "situation": "Sta preparando i cavalli prima della partenza."
                            }
                        ]
                    }
                    3a. **FORMATO OUTPUT**
                    - DEVI restituire SOLAMENTE il JSON strutturato come specificato sopra.
                    - Non aggiungere testo esplicativo, commenti o markdown.
                    - Il JSON deve essere valido e parsabile.
                    
                    Esempio di output:
                    {"characters": [{"name": "Anna", "role": "protagonista", ...}]}
    """),
    model=PRO_MODEL,
    disallow_transfer_to_parent=False,
    output_key="characters_data"
    )

# . AMBIENTATION RECOGNITION AGENT
ambient_recognition_agent=LlmAgent(
    name="AmbientRecognitionAgent",
    description="Un agente Che identifica e descrive l'ambientazione in cui ha luogo il racconto.",
    instruction=('''
                 Sei un agente che si occupa di identificare e descrivere le ambientazioni presenti nel racconto. I tuoi compiti sono i seguenti:

                1. **RICONOSCIMENTO AMBIENTI**

         
                Analizza il racconto ed estraine le ambientazioni principali in cui si svolgono gli eventi.

                Comprendi se una descrizione si riferisce a una parte o a una prospettiva diversa di un'ambientazione già esistente (es. "la torre più alta del castello" è parte del "Castello di Eldoria", "la cucina" è una stanza della "Casa dei protagonisti") e non crearne una nuova.

                Considera sia luoghi fisici (naturali o artificiali) che dimensioni astratte o oniriche (es. il "Paese delle Meraviglie", il "Piano Astrale").

                Se il testo è breve, includi anche le ambientazioni menzionate indirettamente (es. “la città da cui sono fuggiti”, “la foresta proibita oltre il confine”).

                2. **ANALISI E DESCRIZIONE**

                Per ogni ambientazione individuata, fornisci nella lista:

                Nome o designazione: (es. “Foresta di Sherwood”, “La taverna del Drago Ubriaco”, “Pianeta Desertico Arrakis")

                Ruolo narrativo: principale / secondaria / simbolica / cornice

                Caratteristiche fisiche e atmosfera: Geografia, architettura, clima, illuminazione, colori predominanti, suoni, odori, stato di conservazione (es. antico e decadente, moderno e sterile).

                Impatto sulla storia: In che modo influenza la trama o i personaggi? (es. crea tensione, ispira pace, ostacola il viaggio, definisce la società).

                Eventi significativi: Quali avvenimenti cruciali vi hanno luogo? (es. "l'incontro segreto", "la battaglia finale", "la scoperta decisiva").

                Citazione o dettaglio chiave (opzionale): Un frammento del testo che la descrive efficacemente.

                Periodo di tempo o era: (es. "epoca vittoriana", "anno 3024", "era medievale", "tempo presente").

                3. **SALVATAGGIO DELLE INFORMAZIONI**

                Devi salvare le informazioni ottenute in un file JSON con il seguente formato strutturato:
                {
                    "ambients": [
                        {
                            "name": "Villaggio di montagna",
                            "description": "Un piccolo villaggio di pietra situato tra le montagne, immerso nel silenzio del tramonto.",
                            "time_period": "Tardo pomeriggio, epoca imprecisata ma pre-industriale.",
                            "atmosphere": "Tranquilla e malinconica, con una leggera tensione nell’aria.",
                            "key_elements": ["case di pietra", "sentieri sterrati", "camini fumanti", "vento freddo"],
                            "associated_characters": ["Anna", "Marco"],
                            "relevant_scenes": ["Scena 1 – prima parte (prime 1000 battute)"],
                            "narrative_role": "Luogo di partenza del viaggio, simbolo delle origini e della sicurezza perduta."
                        },
                        {
                            "name": "Strada di montagna nella nebbia",
                            "description": "Un sentiero tortuoso tra le rocce, avvolto da una fitta nebbia che nasconde il paesaggio circostante.",
                            "time_period": "Mattino presto, giorno successivo alla partenza.",
                            "atmosphere": "Misteriosa e inquieta.",
                            "key_elements": ["nebbia fitta", "strada sterrata", "eco lontano", "odore di terra bagnata"],
                            "associated_characters": ["Anna", "Marco", "Il viandante"],
                            "relevant_scenes": ["Scena 2 – seconda parte (battute 1001-2000)"],
                            "narrative_role": "Luogo di transizione e inizio del viaggio verso l’ignoto."
                        }
                    ]
                }
                    '''
        ),
    model=PRO_MODEL,
    disallow_transfer_to_parent=False,
    output_key="ambientation_data"
)

# . SCENE RECOGNITION AGENT
scene_recognition_agent = LlmAgent(
    name="SceneRecognitionAgent",
    description="Sceneggiatore specializzato nell'analisi, descrizione e divisione delle scene di un racconto.",
    instruction=("""
                 1. **INDIVIDUAZIONE DELLE SCENE**   
                    - Analizza il racconto e suddividilo in scene distinte DI CIRCA 1000 BATTUTE basate su cambiamenti di ambientazione, tempo, personaggi coinvolti o tono narrativo.
                 
                 2. **ANALISI E DESCRIZIONE**

                    Per ogni scena individuata, fornisci nella lista:

                    - Numero e posizione: (es. "Scena 1 – prima parte (prime 1000 battute)")
                    - Ambientazione: luogo, tempo, atmosfera (es. "un villaggio di montagna al tramonto")
                    - Personaggi presenti: elenco sintetico dei personaggi che partecipano
                    - Azione principale: breve riassunto degli eventi chiave
                    - Tono e ritmo: (es. concitato, malinconico, onirico, tranquillo, ecc.)
                    - Emozioni predominanti: (es. paura, speranza, rabbia, nostalgia…)
                    - Citazione o dettaglio rappresentativo (opzionale): un frammento del testo che rappresenta bene la scena
                    - Funzione narrativa: (es. introduzione, sviluppo, climax, risoluzione, epilogo, flashback, ecc.)

                    3. **SALVATAGGIO DELLE INFORMAZIONI**

                    - Devi salvare le informazioni ottenute in formato josn seguendo questa struttura:
                 {
                    "scenes": [
                        {
                            "number_and_position": "Scena 1 – prima parte (prime 1000 battute)",
                            "setting": "Un villaggio di montagna al tramonto, tra le case di pietra e il rumore del vento.",
                            "characters_present": ["Anna", "Marco"],
                            "main_action": "Anna e Marco discutono sul viaggio imminente mentre preparano i cavalli.",
                            "tone_and_rhythm": "Tranquillo ma con una tensione crescente.",
                            "dominant_emotions": ["determinazione", "nostalgia"],
                            "representative_quote": "«Forse non torneremo mai più qui.»",
                            "narrative_function": "Introduzione"
                        },
                        {
                            "number_and_position": "Scena 2 – seconda parte (battute 1001-2000)",
                            "setting": "La strada di montagna immersa nella nebbia del mattino.",
                            "characters_present": ["Anna", "Marco", "Il viandante"],
                            "main_action": "I due incontrano un viandante misterioso che offre loro indicazioni ambigue.",
                            "tone_and_rhythm": "Misterioso e sospeso.",
                            "dominant_emotions": ["curiosità", "sospetto"],
                            "representative_quote": "«La strada giusta non sempre è quella più chiara.»",
                            "narrative_function": "Sviluppo"
                        }
                    ]
                }

"""),
    model=PRO_MODEL,
    disallow_transfer_to_parent=False,
    output_key="scenes_data"
)

# -----TUTTI I MODELLI SOPRA SALVANO I RISULTATI NELLE OUTPUT_KEY COME JSON----- #

# . CHARACTER IMAGE AGENT
character_image_agent = LlmAgent(
    name="CharacterImageAgent",
    description="Crea illustrazioni base dei personaggi principali.",
    instruction=(
        "Ricevi in input una lista di personaggi con le loro descrizioni testuali e lo stile artistico stabilito per la storia. "
        "Per ogni personaggio, genera un'immagine di riferimento in posa neutra, centrata sul corpo intero o mezzo busto, "
        "che metta in evidenza i tratti principali (aspetto fisico, abbigliamento, colori distintivi e accessori rilevanti). "
        "Le immagini devono avere sfondo neutro e mantenere coerenza stilistica con lo stile fornito. "
        "Ogni immagine deve servire come base visiva per le fasi successive della pipeline di generazione delle scene, "
        "quindi evita elementi narrativi o dinamici. "
        "Assicurati che tutte le immagini condividano lo stesso livello di dettaglio, illuminazione e impostazione visiva."
    ),
    model=IMAGE_MODEL,
    after_model_callback=character_after_model_callback
)

# . AMBIENTATION IMAGE AGENT
ambientation_image_agent = LlmAgent(
    name="CharacterImageAgent",
    description="Crea illustrazioni base dei personaggi principali.",
    instruction=(
        "Ricevi in input una lista di personaggi con le loro descrizioni testuali e lo stile artistico stabilito per la storia. "
        "Per ogni personaggio, genera un'immagine di riferimento in posa neutra, centrata sul corpo intero o mezzo busto, "
        "che metta in evidenza i tratti principali (aspetto fisico, abbigliamento, colori distintivi e accessori rilevanti). "
        "Le immagini devono avere sfondo neutro e mantenere coerenza stilistica con lo stile fornito. "
        "Ogni immagine deve servire come base visiva per le fasi successive della pipeline di generazione delle scene, "
        "quindi evita elementi narrativi o dinamici. "
        "Assicurati che tutte le immagini condividano lo stesso livello di dettaglio, illuminazione e impostazione visiva."
    ),
    model=IMAGE_MODEL,
    after_model_callback=ambientation_after_model_callback
)

# ----- QUESTI DUE MODELLI SALVANO LE IMMAGINI NEGLI ARTIFACT UTILIZZANDO I CALLBACK AFTER MODEL (SALVATI IN MEMORY) ----- #

# . ILLUSTRATOR AGENT
illustrator_agent = LlmAgent(
    name="IllustratorAgent",
    description="Crea illustrazioni complete delle scene basandosi sulle descrizioni, i personaggi e le ambientazioni.",
    instruction=(
        "Ricevi in input:\n"
        "- La lista delle scene con descrizioni, tono e azioni.\n"
        "- Le immagini base dei personaggi e delle ambientazioni.\n\n"
        "Per ogni scena, genera un’illustrazione coerente che rappresenti i personaggi coinvolti "
        "nell’ambiente indicato, rispettando lo stile visivo fornito.\n"
        "Assicurati di mantenere continuità di luce, prospettiva e colore rispetto ai concept base."
    ),
    model=IMAGE_MODEL,
    before_model_callback=illustrator_before_model_callback
)

# ----- QUESTO MODELLO PRENDE LE INFORMAZIONI DALLE OUTPUT_KEY DI SCENE RECOGNITION AGENT (SCENE_DATA) E GLI ARTIFACT DEI MODELLI DI IMMAGINE PER CREARE LE ILLUSTRAZIONI ---- #

coordinator_agent.sub_agents = [
    scene_recognition_agent,
    character_recognition_agent,
    ambient_recognition_agent,
    character_image_agent,
    ambientation_image_agent,
    illustrator_agent
]