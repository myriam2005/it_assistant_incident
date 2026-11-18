import json
from pathlib import Path

from langchain_core.tools import tool
import re
# tools/ -> it_incident_assistant/ -> src/ -> racine du projet
DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def load_json(filename: str):
    """Charge une liste d'objets depuis un fichier JSON local."""
    path = DATA_DIR / filename
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)



STOPWORDS = {
    "que", "qui", "quoi", "dit", "des", "les", "une", "est", "sur", "dans",
    "pour", "avec", "pas", "mon", "mes", "ton", "ses", "son", "et", "web",
    "the", "and", "for",
}


def contains_query(text: str, query: str) -> bool:
    """Au moins un mot utile de la requête doit apparaître comme mot entier."""
    terms = [
        w for w in re.findall(r"\w+", query.lower())
        if len(w) > 2 and w not in STOPWORDS
    ]
    words_in_text = set(re.findall(r"\w+", text.lower()))
    return any(term in words_in_text for term in terms)

def search_in(filename: str, query: str, empty_message: str) -> str:
    """Cherche dans un fichier JSON et renvoie les résultats en texte."""
    matches = []
    for entry in load_json(filename):
        searchable = " ".join(str(value) for value in entry.values())
        if contains_query(searchable, query):
            matches.append(entry)
    if not matches:
        return empty_message
    return json.dumps(matches, ensure_ascii=False, indent=2)


@tool
def search_logs(query: str) -> str:
    """Recherche des erreurs ou événements pertinents dans les logs IT locaux.
    Utiliser cet outil pour trouver des messages liés à un incident.
    """
    return search_in("logs.json", query, "Aucun log correspondant trouvé.")


@tool
def search_incidents(query: str) -> str:
    """Recherche des incidents historiques similaires et leurs résolutions."""
    return search_in("incidents.json", query, "Aucun incident similaire trouvé.")


@tool
def search_documentation(query: str) -> str:
    """Recherche des procédures et documents techniques pertinents."""
    return search_in("documentation.json", query, "Aucun document correspondant trouvé.")


TOOLS = [search_logs, search_incidents, search_documentation]
