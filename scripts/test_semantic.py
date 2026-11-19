import json

from it_incident_assistant.tools.semantic_tools import (
    search_documentation,
    search_incidents,
    search_logs,
)

questions = [
    "le serveur web tourne une erreur 502",
    "l app est lente , les connexions a la bd sont saturés",
    "mon imprimente ne fonctionne plus",
]

for q in questions:
    print("\n" + "=" * 60)
    print("QUESTION :", q)
    for tool_fn in (search_logs, search_incidents, search_documentation):
        out = tool_fn.invoke(q)
        if out.startswith("["):
            ids = [e.get("id") or e.get("title") or e.get("message") for e in json.loads(out)]
            print(f"  {tool_fn.name}: {ids}")
        else:
            print(f"  {tool_fn.name}: {out}")