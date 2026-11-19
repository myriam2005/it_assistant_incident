from it_incident_assistant.agent.graph import graph

config = {"configurable": {"thread_id": "test-001"}}

result = graph.invoke(
    {"messages": [("user", "le serveur web tourne une erreur 502.")]},
    config=config,
)

for message in result["messages"]:
    print("\nTYPE :", type(message).__name__)
    print("CONTENU :", message.content)
    if getattr(message, "tool_calls", None):
        print("OUTILS DEMANDÉS :", message.tool_calls)