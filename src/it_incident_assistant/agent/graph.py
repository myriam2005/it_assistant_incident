import importlib
import os
import uuid

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from it_incident_assistant.tools.knowledge_tools import search_knowledge

load_dotenv()

# Logs et incidents : "semantic" (V2) ou "keyword" (V1)
SEARCH_MODE = os.getenv("SEARCH_MODE", "semantic")
_module_name = "semantic_tools" if SEARCH_MODE == "semantic" else "incident_tools"
_tools_module = importlib.import_module(f"it_incident_assistant.tools.{_module_name}")

search_logs = _tools_module.search_logs
search_incidents = _tools_module.search_incidents

# La documentation vient des runbooks (search_knowledge)
TOOLS = [search_logs, search_incidents, search_knowledge]

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not api_key:
    raise ValueError("GROQ_API_KEY est absente. Vérifie ton fichier .env.")

llm = ChatGroq(model=model_name, temperature=0, api_key=api_key)
llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = """
Tu es un assistant de diagnostic informatique (IT Incident Assistant).

Les résultats de trois sources (search_logs, search_incidents,
search_knowledge) sont déjà dans la conversation, résumés dans un message
"Résultats des recherches". Chaque source y est marquée VIDE ou
RÉSULTATS PRÉSENTS. Tu peux relancer un outil avec d'autres mots-clés
anglais courts si les résultats sont insuffisants.

Règles strictes :
- Utilise UNIQUEMENT les informations présentes dans les résultats des outils.
- Une source marquée RÉSULTATS PRÉSENTS doit être utilisée dans la section
  correspondante. Tu n'écris "Aucun ... trouvé" que pour une source marquée VIDE.
- N'écris AUCUNE commande shell, AUCUN chemin de fichier, AUCUN nom de
  fichier de configuration : ils ne figurent pas dans les sources.
- Ne recommande une action que si elle apparaît dans l'incident ou un
  passage de runbook, et reprends ses mises en garde (ex. autorisation requise).
- N'utilise pas tes connaissances générales pour combler un vide.
- Si la demande n'est pas un incident technique, réponds normalement.
- Ne prétends jamais avoir exécuté une action sur un vrai serveur.
- Si les trois sources sont VIDES, réponds uniquement que les sources
  locales ne contiennent rien, et invite l'utilisateur à donner plus de
  détails ou à contacter un technicien.
- Attribue chaque information à son vrai outil : les logs viennent de
  search_logs, les incidents de search_incidents, les procédures de
  search_knowledge. Pour un passage de runbook, utilise uniquement sa
  citation exacte [fichier > section], telle qu'elle apparaît dans le champ
  "citation". Ne cite jamais une source absente des résultats.
- Cite chaque passage de runbook une seule fois.
- Quand tu appuies une hypothèse sur un incident, reprends sa cause telle
  qu'elle est écrite, sans la reformuler ni l'étendre.

Format (court, sans tableau) :
1. Faits observés (logs)
2. Incidents similaires (ID, cause, résolution)
3. Procédure documentée (passages avec citation [fichier > section])
4. Hypothèses (maximum 2, marquées "à vérifier", chacune appuyée par un
   fait, un incident ou un passage cité ; si aucune source n'a été
   trouvée, écris "Aucune hypothèse possible sans données" et n'en
   propose pas)
5. Limites des sources

Réponds en français.
"""

LABELS = {
    "search_logs": "LOGS",
    "search_incidents": "INCIDENTS",
    "search_knowledge": "RUNBOOKS",
}


def gather_node(state: MessagesState):
    """Lance systématiquement les trois recherches et résume les résultats."""
    question = state["messages"][-1].content
    calls = []
    results = []
    for tool_fn in (search_logs, search_incidents, search_knowledge):
        call_id = f"gather-{uuid.uuid4().hex[:8]}"
        calls.append(
            {"name": tool_fn.name, "args": {"query": question}, "id": call_id, "type": "tool_call"}
        )
        results.append(
            ToolMessage(content=tool_fn.invoke(question), tool_call_id=call_id, name=tool_fn.name)
        )

    # Étiquette calculée par le code : le modèle n'a plus à deviner si une source est vide
    summary = "\n\n".join(
        f"=== {LABELS[m.name]} ({'VIDE' if m.content.startswith('Aucun') else 'RÉSULTATS PRÉSENTS'}) ===\n{m.content}"
        for m in results
    )
    return {
        "messages": [AIMessage(content="", tool_calls=calls)]
        + results
        + [HumanMessage(content=f"Résultats des recherches :\n\n{summary}")]
    }


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