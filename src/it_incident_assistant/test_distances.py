import sys

import chromadb
from fastembed import TextEmbedding

from it_incident_assistant.tools.semantic_tools import DB_DIR, MODEL_NAME

# Sans argument : on teste tes deux phrases avec fautes, plus l'imprimante.
DEFAULTS = [
    "le serveur web tourne une erreur 502",
    "l app est lente , les connexions a la bd sont saturés",
    "mon imprimente ne fonctionne plus",
]
questions = sys.argv[1:] or DEFAULTS

model = TextEmbedding(MODEL_NAME)
client = chromadb.PersistentClient(path=str(DB_DIR))

for q in questions:
    print("\nQUESTION :", q)
    vec = next(iter(model.embed([q]))).tolist()
    for name in ("logs", "incidents", "documentation"):
        res = client.get_collection(name).query(
            query_embeddings=[vec], n_results=4, include=["documents", "distances"]
        )
        for doc, dist in zip(res["documents"][0], res["distances"][0]):
            print(f"  {dist:.2f}  [{name}] {doc[:70]}")