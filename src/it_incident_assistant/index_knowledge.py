import re
from pathlib import Path

import chromadb
from fastembed import TextEmbedding

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "data" / "docs"
DB_DIR = ROOT / "chroma_db"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION = "knowledge"


def split_markdown(path: Path):
    """Découpe un fichier Markdown en passages, un par section '## '."""
    text = path.read_text(encoding="utf-8")

    title_match = re.search(r"^# (.+)$", text, flags=re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else path.stem

    kw_match = re.search(r"^Keywords: (.+)$", text, flags=re.MULTILINE)
    keywords = kw_match.group(1).strip() if kw_match else ""

    passages = []
    # Le premier morceau (titre + Keywords) précède le premier '## ' : ignoré
    parts = re.split(r"^## ", text, flags=re.MULTILINE)[1:]
    for part in parts:
        heading, _, body = part.partition("\n")
        body = " ".join(body.split())
        if not body:
            continue
        passages.append(
            {
                "source": path.name,
                "doc_title": doc_title,
                "keywords": keywords,
                "section": heading.strip(),
                "text": body,
            }
        )
    return passages


def main():
    passages = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        passages.extend(split_markdown(path))

    print(f"{len(passages)} passages trouvés :")
    for p in passages:
        print(f"  - {p['source']} > {p['section']} ({len(p['text'])} caractères)")

    # Texte vectorisé : titre + mots-clés (FR/EN) + section + contenu
    to_embed = [
        f"{p['doc_title']} ({p['keywords']}) - {p['section']}. {p['text']}"
        for p in passages
    ]

    model = TextEmbedding(MODEL_NAME)
    vectors = [v.tolist() for v in model.embed(to_embed)]

    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    collection.add(
        ids=[f"{p['source']}#{i}" for i, p in enumerate(passages)],
        documents=[p["text"] for p in passages],
        embeddings=vectors,
        metadatas=[
            {"source": p["source"], "doc_title": p["doc_title"], "section": p["section"]}
            for p in passages
        ],
    )
    print(f"\nCollection '{COLLECTION}' : {collection.count()} passages indexés")


if __name__ == "__main__":
    main()