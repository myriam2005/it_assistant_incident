import json
from pathlib import Path

import chromadb
from fastembed import TextEmbedding

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DB_DIR = ROOT / "chroma_db"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

SOURCES = {
    "logs": "logs.json",
    "incidents": "incidents.json",
    "documentation": "documentation.json",
}


def to_text(entry: dict) -> str:
    """Concatène les champs texte d'une entrée (listes incluses)."""
    parts = []
    for value in entry.values():
        if isinstance(value, list):
            parts.append(", ".join(str(v) for v in value))
        else:
            parts.append(str(value))
    return " | ".join(parts)


def main():
    model = TextEmbedding(MODEL_NAME)
    client = chromadb.PersistentClient(path=str(DB_DIR))

    for name, filename in SOURCES.items():
        entries = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        texts = [to_text(e) for e in entries]
        vectors = [v.tolist() for v in model.embed(texts)]

        # On recrée la collection pour pouvoir relancer le script sans doublons
        try:
            client.delete_collection(name)
        except Exception:
            pass
        collection = client.create_collection(name, metadata={"hnsw:space": "cosine"})

        collection.add(
            ids=[f"{name}-{i}" for i in range(len(entries))],
            documents=[json.dumps(e, ensure_ascii=False) for e in entries],
            embeddings=vectors,
        )
        print(f"{name}: {collection.count()} documents indexés")


if __name__ == "__main__":
    main()