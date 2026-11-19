import os
import uuid

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
import importlib

load_dotenv()


SEARCH_MODE = os.getenv("SEARCH_MODE", "semantic")  # "semantic" ou "keyword"
_module_name = "semantic_tools" if SEARCH_MODE == "semantic" else "incident_tools"
_tools_module = importlib.import_module(f"it_incident_assistant.tools.{_module_name}")

TOOLS = _tools_module.TOOLS
search_logs = _tools_module.search_logs
search_incidents = _tools_module.search_incidents
search_documentation = _tools_module.search_documentation
api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not api_key:
    raise ValueError("GROQ_API_KEY est absente. Vérifie ton fichier .env.")

llm = ChatGroq(model=model_name, temperature=0, api_key=api_key)
llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = """
Tu es un assistant de diagnostic informatique (IT Incident Assistant).

Les résultats des trois sources (logs, incidents, documentation) sont déjà
dans la conversation. Tu peux relancer un outil avec d'autres mots-clés
anglais courts si les résultats sont insuffisants.

Règles strictes :
- Utilise UNIQUEMENT les informations présentes dans les résultats des outils.
- N'écris AUCUNE commande shell, AUCUN chemin de fichier, AUCUN nom de
  fichier de configuration : ils ne figurent pas dans les sources.
- Ne recommande une action que si elle apparaît dans l'incident ou la
  documentation, et reprends ses mises en garde (ex. autorisation requise).
- Si un résultat est "Aucun ... trouvé", dis que les sources ne contiennent
  pas d'information sur ce point. N'utilise pas tes connaissances générales
  pour combler le vide.
- Si la demande n'est pas un incident technique, réponds normalement.
- Ne prétends jamais avoir exécuté une action sur un vrai serveur.
- Si les trois recherches sont vides, réponds uniquement que les sources
  locales ne contiennent rien, et invite l'utilisateur à donner plus de
  détails ou à contacter un technicien.
- Lis chaque résultat d'outil avant d'écrire. Si un résultat contient des
  données (un log, un incident, un document), tu dois l'utiliser dans la
  section correspondante. N'écris "Aucun ... trouvé" que si le résultat de
  l'outil est exactement "Aucun ... trouvé".
Format (court, sans tableau) :
1. Faits observés (logs)
2. Incidents similaires (ID, cause, résolution)
3. Procédure documentée (titre et contenu)
4. Hypothèses (maximum 2, marquées "à vérifier", chacune appuyée par un
   fait ou un incident cité ; si aucune source n'a été trouvée, écris
   "Aucune hypothèse possible sans données" et n'en propose pas)
5. Limites des sources

Réponds en français.
"""


def gather_node(state: MessagesState):
    """Lance les trois recherches de façon systématique."""
    question = state["messages"][-1].content
    calls = []
    results = []
    for tool_fn in (search_logs, search_incidents, search_documentation):
        call_id = f"gather-{uuid.uuid4().hex[:8]}"
        calls.append({"name": tool_fn.name, "args": {"query": question}, "id": call_id, "type": "tool_call"})
        results.append(ToolMessage(content=tool_fn.invoke(question), tool_call_id=call_id, name=tool_fn.name))
    return {"messages": [AIMessage(content="", tool_calls=calls)] + results}


def agent_node(state: MessagesState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("gather", gather_node)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(TOOLS))

builder.add_edge(START, "gather")
builder.add_edge("gather", "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)