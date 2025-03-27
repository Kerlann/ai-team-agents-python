#!/usr/bin/env python3
"""
Point d'entrée principal pour l'équipe d'agents IA.
"""

import sys
import os
import argparse
from pathlib import Path

# Ajouter le répertoire parent au path pour permettre les imports relatifs
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.team.team import AITeam
from src.utils.logger import setup_logger
import config


def parse_arguments():
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(description="Équipe d'agents IA pour le développement logiciel")
    parser.add_argument(
        "--task", "-t",
        type=str,
        help="Tâche à soumettre à l'équipe"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Mode interactif pour soumettre plusieurs tâches"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Chemin où sauvegarder les résultats"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Affiche les messages de debug"
    )
    return parser.parse_args()


def setup_environment():
    """Configure l'environnement d'exécution."""
    # Créer les répertoires nécessaires
    os.makedirs(config.HISTORY_CONFIG["history_dir"], exist_ok=True)
    
    # Configuration de la journalisation
    log_level = "DEBUG" if parse_arguments().verbose else config.LOGGING["level"]
    setup_logger(log_level, config.LOGGING["format"], config.LOGGING["file"])


def interactive_mode():
    """Exécute le programme en mode interactif."""
    team = AITeam()
    print("=== Mode interactif - Équipe d'agents IA ===")
    print("Entrez 'exit' ou 'quit' pour quitter")
    
    while True:
        task = input("\nEntrez votre tâche : ")
        if task.lower() in ["exit", "quit"]:
            break
        
        if not task.strip():
            continue
            
        print("\nTraitement en cours...")
        result = team.solve_task(task)
        
        print("\n=== RÉSULTAT ===\n")
        if result:
            print(result)
        else:
            print("Aucun résultat généré. Vérifiez les journaux pour plus d'informations.")


def execute_single_task(task, output_path=None):
    """Exécute une seule tâche."""
    team = AITeam()
    result = team.solve_task(task)
    
    print("\n=== RÉSULTAT ===\n")
    if result:
        try:
            # Utiliser des print pour éviter les problèmes d'affichage
            result_lines = result.split('\n')
            for line in result_lines:
                print(line)
        except Exception as e:
            print(f"Erreur lors de l'affichage du résultat: {e}")
            print(f"Longueur du résultat: {len(result)}")
            print(f"Début du résultat: {result[:200]}...")
    else:
        print("Aucun résultat généré. Vérifiez les journaux pour plus d'informations.")
    
    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result if result else "Aucun résultat généré")
            print(f"\nRésultat sauvegardé dans {output_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du résultat: {e}")


def main():
    """Fonction principale."""
    setup_environment()
    args = parse_arguments()
    
    if args.interactive:
        interactive_mode()
    elif args.task:
        execute_single_task(args.task, args.output)
    else:
        print("Aucune tâche spécifiée. Utilisez --task ou --interactive")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
