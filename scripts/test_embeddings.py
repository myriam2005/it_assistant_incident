import numpy as np
from fastembed import TextEmbedding

model = TextEmbedding("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

query = "Le serveur web retourne une erreur 502"
docs = [
    "HTTP 502 Bad Gateway: upstream connection refused",
    "Database connection pool usage is high",
    "Gateway process started",
]
other = "Mon imprimante ne fonctionne plus"


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


qv = np.array(list(model.embed([query]))[0])
print("QUESTION :", query)
for d, v in zip(docs, model.embed(docs)):
    print(f"  {cos(qv, np.array(v)):.2f}  {d}")

ov = np.array(list(model.embed([other]))[0])
print("\nQUESTION :", other)
for d, v in zip(docs, model.embed(docs)):
    print(f"  {cos(ov, np.array(v)):.2f}  {d}")