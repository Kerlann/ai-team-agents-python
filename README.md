# Équipe d'Agents IA de Développement

Ce projet implémente une équipe d'agents d'intelligence artificielle composée d'un manager et de deux développeurs qui collaborent pour résoudre des problèmes de programmation.

## Structure de l'Équipe

- **Manager** : Supervise le travail, délègue les tâches, évalue les résultats et coordonne l'équipe
- **Développeur Frontend** : Spécialisé dans le développement d'interfaces utilisateur
- **Développeur Backend** : Spécialisé dans la logique métier et les systèmes backend

## Fonctionnalités

- Communication entre agents via un système de messagerie
- Décomposition automatique des tâches complexes
- Utilisation de modèles de langage locaux via Ollama
- Architecture extensible pour ajouter de nouveaux agents
- Gestion de l'historique des conversations et des contextes

## Prérequis

- Python 3.9+
- Ollama installé localement (https://ollama.ai/)
- Un modèle de langage compatible (ex: mistral, llama2, etc.)

## Installation

1. Cloner ce dépôt
   ```bash
   git clone https://github.com/Kerlann/ai-team-agents-python.git
   cd ai-team-agents-python
   ```

2. Créer un environnement virtuel Python
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. Installer les dépendances
   ```bash
   pip install -r requirements.txt
   ```

4. Configurer Ollama
   ```bash
   # Vérifiez que Ollama est installé et en cours d'exécution
   # Puis téléchargez un modèle, par exemple:
   ollama pull mistral
   ```

## Utilisation

1. Démarrer l'équipe d'agents
   ```bash
   python src/main.py
   ```

2. Configuration
   - Modifier le fichier `config.py` pour personnaliser les paramètres et les prompts des agents

## Exemples d'utilisation

```python
from team import AITeam

# Créer une équipe
team = AITeam()

# Soumettre une tâche à l'équipe
result = team.solve_task("Créer une application simple de liste de tâches avec une API REST et une interface web")

# Afficher le résultat
print(result)
```

## Structure du projet

```
├── src/
│   ├── main.py              # Point d'entrée principal
│   ├── agents/              # Implémentation des agents
│   │   ├── agent.py         # Classe de base pour les agents
│   │   ├── manager.py       # Agent manager
│   │   ├── frontend_dev.py  # Agent développeur frontend
│   │   └── backend_dev.py   # Agent développeur backend
│   ├── llm/                 # Module d'interface avec les modèles de langage
│   │   └── ollama_client.py # Interface avec Ollama
│   ├── team/                # Module de gestion d'équipe
│   │   ├── team.py          # Classe AITeam pour gérer l'équipe
│   │   └── message.py       # Système de messagerie entre agents
│   └── utils/               # Utilitaires
│       ├── logger.py        # Journalisation
│       └── prompts.py       # Templates de prompts
├── config.py                # Configuration globale
├── requirements.txt         # Dépendances Python
└── README.md                # Documentation
```

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à proposer une pull request.

## Licence

Ce projet est sous licence MIT.
