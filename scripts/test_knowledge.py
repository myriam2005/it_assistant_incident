import sys

from it_incident_assistant.tools.knowledge_tools import search_knowledge

DEFAULTS = [
    "le serveur web retourne une erreur 502",
    "puis-je redémarrer le service ?",
    "l app est lente, les connexions a la bd sont saturées",
    "le disque est plein",
    "mon imprimante ne fonctionne plus",
]

for q in sys.argv[1:] or DEFAULTS:
    print("\n" + "=" * 60)
    print("QUESTION :", q)
    out = search_knowledge.invoke(q)
    if out.startswith("["):
        import json
        for p in json.loads(out):
            print(f"  {p['citation']}  {p['passage'][:70]}...")
    else:
        print(" ", out)