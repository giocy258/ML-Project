def load_markdown_content(file_path: str, variables: dict = None) -> str:
    """
    Legge un file Markdown.
    Se viene passato 'variables', esegue la formattazione (utile per le istruzioni dinamiche).
    Se 'variables' è None, restituisce il testo puro (utile per description statiche).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if variables:
            # Inietta le variabili (es. la data)
            return content.format(**variables)
        else:
            # Restituisce il testo così com'è (sicuro anche se contiene graffe {})
            return content.strip()
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Il file '{file_path}' non è stato trovato.")
    except KeyError as e:
        raise ValueError(f"Nel file '{file_path}' manca la variabile per il placeholder: {e}")