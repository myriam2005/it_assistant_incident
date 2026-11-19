import json
from pathlib import Path

import chromadb
from fastembed import TextEmbedding
from langchain_core.tools import tool

ROOT = Path(__file__).resolve().parents[3]
DB_DIR = ROOT / "chroma_db"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Distance cosinus maximale (distance = 1 - similarité).
# 0.70 correspond à une similarité minimale de 0.30.
MAX_DISTANCE = 0.72
MARGIN = 0.12
TOP_K = 3

_model = None
_client = None


def _get_model():
    global _model
    if _model is None:
        _model = TextEmbedding(MODEL_NAME)
    return _model


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(DB_DIR))
    return _client


def search_in(collection_name: str, query: str, empty_message: str) -> str:
    """Recherche sémantique dans une collection, avec seuil de distance."""
    collection = _get_client().get_collection(collection_name)
    vector = next(iter(_get_model().embed([query]))).tolist()
    result = collection.query(
        query_embeddings=[vector],
        n_results=TOP_K,
        include=["documents", "distances"],
    )
    docs = result["documents"][0]
    dists = result["distances"][0]
    matches = []
    if dists and dists[0] <= MAX_DISTANCE:
        limit = min(MAX_DISTANCE, dists[0] + MARGIN)
        matches = [json.loads(d) for d, x in zip(docs, dists) if x <= limit]
    if not matches:
        return empty_message
    return json.dumps(matches, ensure_ascii=False, indent=2)


@tool
def search_logs(query: str) -> str:
    """Recherche des erreurs ou événements pertinents dans les logs IT locaux.
    Utiliser cet outil pour trouver des messages liés à un incident.
    """
    return search_in("logs", query, "Aucun log correspondant trouvé.")


@tool
def search_incidents(query: str) -> str:
    """Recherche des incidents historiques similaires et leurs résolutions."""
    return search_in("incidents", query, "Aucun incident similaire trouvé.")


@tool
def search_documentation(query: str) -> str:
    """Recherche des procédures et documents techniques pertinents."""
    return search_in("documentation", query, "Aucun document correspondant trouvé.")


TOOLS = [search_logs, search_incidents, search_documentation]