from it_incident_assistant.agent.graph import graph


def main():
    print("=" * 55)
    print("IT INCIDENT ASSISTANT — V3")
    print("Décris un incident informatique. Tape 'quit' pour sortir.")
    print("=" * 55)

    # Un identifiant stable permet de retrouver le même fil de conversation.
    thread_id = "demo-session-001"
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        question = input("\nToi : ").strip()

        if question.lower() in {"quit", "exit", "q"}:
            print("Fin de la session.")
            break

        if not question:
            continue

        try:
            result = graph.invoke(
                {"messages": [("user", question)]},
                config=config,
            )
            final_message = result["messages"][-1]
            print("\nAssistant :")
            print(final_message.content)
        except Exception as error:
            print(f"\nUne erreur est survenue : {error}")


if __name__ == "__main__":
    main()