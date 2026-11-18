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

## Exemples d'exécution

Colle ici tes deux sorties : le test 502 et le test base de données.
