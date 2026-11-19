import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from it_incident_assistant.tools.incident_tools import TOOLS

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

llm_with_tools = llm.bind_tools(TOOLS)

questions = [
    "Mon serveur web retourne une erreur 502.",
    "L'application est lente et la base de données semble saturée.",
    "Mon imprimante ne fonctionne plus.",
    "Bonjour, comment ça va ?",
]

for question in questions:
    print("\n" + "=" * 60)
    print("QUESTION :", question)
    response = llm_with_tools.invoke(question)
    print("CONTENU  :", response.content)
    print("TOOL CALLS :", response.tool_calls)