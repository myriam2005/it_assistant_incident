from it_incident_assistant.tools.incident_tools import (
    search_logs,
    search_incidents,
    search_documentation,
)

print("=== LOGS : 502 ===")
print(search_logs.invoke("502"))

print("\n=== INCIDENTS : database pool ===")
print(search_incidents.invoke("database pool"))

print("\n=== DOC : upstream backend ===")
print(search_documentation.invoke("upstream backend"))

print("\n=== SUJET INCONNU : imprimante ===")
print(search_logs.invoke("imprimante"))