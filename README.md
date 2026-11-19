# IT Incident Assistant V1

Agent de diagnostic IT : il reçoit un incident, consulte trois sources
locales (logs, incidents historiques, documentation) et rédige un
diagnostic fondé uniquement sur les résultats trouvés.

## Installation

```bash
uv sync
```

Crée un fichier `.env` à la racine :

```
GROQ_API_KEY=ta_cle_api
GROQ_MODEL=openai/gpt-oss-120b
```

## Lancement

```bash
uv run python -m it_incident_assistant.main
```

## Architecture

```
START -> gather -> agent -> (tools -> agent)* -> fin
```

- `gather` : lance toujours les trois recherches (logs, incidents,
  documentation), pour ne pas dépendre du choix du modèle.
- `agent` : le LLM rédige le diagnostic et peut relancer un outil.
- `tools` : exécute les outils demandés (ToolNode).
- Mémoire : InMemorySaver, un fil par `thread_id`, perdu à l'arrêt.

## Limites de la V1

- Recherche par mots-clés exacts, sans sémantique (V2 : embeddings).
- Données fictives, aucune action sur un vrai serveur.
- Le diagnostic doit être vérifié par un humain.

## V2 : recherche sémantique

La V1 cherchait des mots exacts. La V2 utilise des embeddings
multilingues (fastembed, `paraphrase-multilingual-MiniLM-L12-v2`) et
ChromaDB : une question en français retrouve des données en anglais.

Indexation (à relancer si les JSON changent) :

```bash
uv run python -m it_incident_assistant.index_data
```

Choix de la méthode dans `.env` :

```
SEARCH_MODE=semantic   # ou keyword (V1)
```

Filtrage des résultats : plafond de distance (0,72) + marge relative
(0,12) par rapport au meilleur résultat. Un seuil fixe ne fonctionnait
pas : avec des phrases mal orthographiées, un bon résultat dépassait le
bruit d'une autre phrase.

Limite : calibré sur 8 documents seulement.
