import json
from pathlib import Path
import re
import chromadb
from fastembed import TextEmbedding
from langchain_core.tools import tool

ROOT = Path(__file__).resolve().parents[3]
DB_DIR = ROOT / "chroma_db"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

MAX_DISTANCE = 0.72   # plafond absolu
MARGIN = 0.12         # écart maximal avec le meilleur passage
TOP_K = 4
RESTRICTIONS = "Escalation and restrictions"

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

GENERIC = {
    "que", "dit", "quoi", "quel", "quelle", "est", "ce", "qui",
    "le", "la", "les", "un", "une", "des", "sur", "runbook", "runbooks",
}


def clean_query(query: str) -> str:
    """Retire les mots génériques qui n'apportent aucun sujet."""
    words = [w for w in re.findall(r"\w+", query.lower()) if w not in GENERIC]
    return " ".join(words) or query
@tool
def search_knowledge(query: str) -> str:
    """Recherche des passages précis dans les runbooks techniques.
    Renvoie les passages pertinents avec leur citation [fichier > section].
    """
    collection = _get_client().get_collection("knowledge")
    vector = next(iter(_get_model().embed([clean_query(query)]))).tolist()
    result = collection.query(
        query_embeddings=[vector],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"],
    )
    docs = result["documents"][0]
    metas = result["metadatas"][0]
    dists = result["distances"][0]

    if not dists or dists[0] > MAX_DISTANCE:
        return "Aucun passage correspondant trouvé."

    limit = min(MAX_DISTANCE, dists[0] + MARGIN)
    selected = [(d, m) for d, m, x in zip(docs, metas, dists) if x <= limit]

    # Si un runbook est pertinent, ses restrictions sont toujours transmises
    sources = {m["source"] for _, m in selected}
    have = {(m["source"], m["section"]) for _, m in selected}
    extra = collection.get(
        where={"section": RESTRICTIONS},
        include=["documents", "metadatas"],
    )
    for d, m in zip(extra["documents"], extra["metadatas"]):
        if m["source"] in sources and (m["source"], m["section"]) not in have:
            selected.append((d, m))

    passages = [
        {
            "citation": f"[{m['source']} > {m['section']}]",
            "runbook": m["doc_title"],
            "passage": d,
        }
        for d, m in selected
    ]
    return json.dumps(passages, ensure_ascii=False, indent=2)