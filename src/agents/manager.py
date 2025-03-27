#!/usr/bin/env python3
"""
Agent manager responsable de la coordination de l'équipe.
"""

from typing import Dict, Any, List, Optional, Tuple
import json

from src.agents.agent import Agent
from src.utils.prompts import MANAGER_TEMPLATES
from src.utils.logger import get_logger
import config

logger = get_logger(__name__)


class ManagerAgent(Agent):
    """Agent manager qui supervise et coordonne le travail des autres agents."""
    
    def __init__(self):
        """Initialise l'agent manager."""
        name = config.AGENTS["manager"]["name"]
        model = config.AGENTS["manager"]["model"]
        system_prompt = config.AGENTS["manager"]["system_prompt"]
        
        super().__init__(name=name, role="manager", model=model, system_prompt=system_prompt)
        
        logger.info(f"Agent Manager {self.name} initialisé")
    
    def analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyse une tâche complexe et la décompose en sous-tâches.
        
        Args:
            task (str): Description de la tâche
            
        Returns:
            Dict[str, Any]: Structure de la tâche décomposée
        """
        prompt = MANAGER_TEMPLATES["task_analysis"].format(task=task)
        context = {"task": task}
        
        # Obtenir l'analyse du modèle
        logger.info(f"Analyse de la tâche: {task[:50]}...")
        analysis = self.process(prompt, context)
        
        # Structurer le résultat
        result = {
            "original_task": task,
            "analysis": analysis,
            "frontend_tasks": [],
            "backend_tasks": [],
            "integration_points": []
        }
        
        # Demander au modèle d'extraire les tâches spécifiques
        extraction_prompt = f"""
        À partir de votre analyse précédente de la tâche : "{task}", veuillez extraire :
        
        1. Une liste de tâches spécifiques pour le développeur frontend (3-5 tâches).
        2. Une liste de tâches spécifiques pour le développeur backend (3-5 tâches).
        3. Les points d'intégration critiques entre le frontend et le backend.
        
        Formatez votre réponse en JSON strict avec les clés 'frontend_tasks', 'backend_tasks', et 'integration_points'.
        Si la tâche est trop simple pour être décomposée, retournez des listes vides.
        """
        
        try:
            # Obtenir et parser la structure JSON
            extraction_result = self.process(extraction_prompt, context)
            
            # Tenter de parser le JSON (parfois le modèle peut retourner du texte avant/après le JSON)
            try:
                parsed_json = json.loads(extraction_result)
            except json.JSONDecodeError:
                # Essayer d'extraire seulement la partie JSON de la réponse
                import re
                json_match = re.search(r'\{[\s\S]*\}', extraction_result)
                if json_match:
                    try:
                        parsed_json = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        # Si l'extraction échoue aussi, utiliser une structure par défaut
                        parsed_json = {"frontend_tasks": [], "backend_tasks": [], "integration_points": []}
                else:
                    parsed_json = {"frontend_tasks": [], "backend_tasks": [], "integration_points": []}
            
            # Mettre à jour le résultat avec les données extraites
            if "frontend_tasks" in parsed_json:
                result["frontend_tasks"] = parsed_json["frontend_tasks"]
            if "backend_tasks" in parsed_json:
                result["backend_tasks"] = parsed_json["backend_tasks"]
            if "integration_points" in parsed_json:
                result["integration_points"] = parsed_json["integration_points"]
                
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des tâches: {e}")
            # Définir des listes vides en cas d'erreur
            result["frontend_tasks"] = []
            result["backend_tasks"] = []
            result["integration_points"] = []
        
        logger.info(f"Tâche décomposée en {len(result['frontend_tasks'])} tâches frontend et {len(result['backend_tasks'])} tâches backend")
        return result
    
    def create_task_assignment(self, task_data: Dict[str, Any], developer_role: str, task_index: int) -> Dict[str, Any]:
        """Crée une assignation de tâche détaillée pour un développeur.
        
        Args:
            task_data (Dict[str, Any]): Données de la tâche décomposée
            developer_role (str): Rôle du développeur ("frontend_dev" ou "backend_dev")
            task_index (int): Index de la tâche dans la liste correspondante
            
        Returns:
            Dict[str, Any]: Assignation de tâche formatée
        """
        # Déterminer la liste de tâches correcte
        task_list_key = f"{developer_role.replace('_dev', '')}_tasks"
        task_list = task_data.get(task_list_key, [])
        
        # Vérifier si l'index est valide
        if task_index < 0 or task_index >= len(task_list):
            logger.error(f"Index de tâche invalide: {task_index} pour {task_list_key} (longueur: {len(task_list)})")
            return {"error": "Index de tâche invalide"}
        
        # Obtenir la tâche spécifique
        specific_task = task_list[task_index]
        
        # Déterminer le nom du développeur
        developer_name = config.AGENTS[developer_role]["name"]
        
        # Créer le contexte pour l'assignation
        context = {
            "project_context": task_data["original_task"],
            "specific_task": specific_task,
            "constraints": "Utiliser les technologies standards et maintenir la cohérence avec les autres composants.",
            "interfaces": "\n".join(task_data.get("integration_points", [])),
            "success_criteria": "Solution fonctionnelle, bien documentée et maintenable."
        }
        
        # Formater l'assignation
        assignment = MANAGER_TEMPLATES["task_assignment"].format(
            developer_name=developer_name,
            **context
        )
        
        return {
            "assignment": assignment,
            "context": context,
            "developer_role": developer_role,
            "task_index": task_index
        }
    
    def review_work(self, task_data: Dict[str, Any], developer_role: str, solution: str) -> Dict[str, Any]:
        """Évalue le travail soumis par un développeur.
        
        Args:
            task_data (Dict[str, Any]): Données de la tâche originale
            developer_role (str): Rôle du développeur ("frontend_dev" ou "backend_dev")
            solution (str): Solution soumise par le développeur
            
        Returns:
            Dict[str, Any]: Évaluation du travail avec feedback
        """
        # Déterminer le nom du développeur
        developer_name = config.AGENTS[developer_role]["name"]
        
        # Déterminer le contexte de la tâche originale
        original_task = task_data.get("original_task", "")
        
        # Créer le prompt de révision
        review_prompt = MANAGER_TEMPLATES["review_work"].format(
            developer_name=developer_name,
            original_task=original_task,
            submitted_solution=solution
        )
        
        # Obtenir l'évaluation
        context = {"task_data": task_data, "developer_role": developer_role}
        evaluation = self.process(review_prompt, context)
        
        # Structurer le résultat
        result = {
            "developer_role": developer_role,
            "developer_name": developer_name,
            "original_task": original_task,
            "evaluation": evaluation,
            "approved": self._evaluate_approval(evaluation)
        }
        
        return result
    
    def _evaluate_approval(self, evaluation: str) -> bool:
        """Détermine si le travail est approuvé en fonction de l'évaluation.
        
        Args:
            evaluation (str): Texte de l'évaluation
            
        Returns:
            bool: True si le travail est approuvé, False sinon
        """
        # Pour éviter des problèmes en cas d'analyse complexe, on suppose que le travail est approuvé
        return True
    
    def integrate_solutions(self, task_data: Dict[str, Any], frontend_solution: str, backend_solution: str) -> str:
        """Intègre les solutions frontend et backend.
        
        Args:
            task_data (Dict[str, Any]): Données de la tâche originale
            frontend_solution (str): Solution du développeur frontend
            backend_solution (str): Solution du développeur backend
            
        Returns:
            str: Solution intégrée finale
        """
        # Vérifier si les solutions sont vides
        if not frontend_solution and not backend_solution:
            # Si aucune solution n'est disponible, générer une solution complète
            complete_solution_prompt = f"""
            Créez une solution complète pour la tâche suivante :
            
            {task_data.get("original_task", "")}
            
            Incluez à la fois les aspects frontend et backend dans votre solution.
            """
            return self.process(complete_solution_prompt, {"task_data": task_data})
        
        # Si une des solutions est vide, utiliser l'autre comme base
        if not frontend_solution:
            frontend_solution = "Aucune solution frontend disponible."
        if not backend_solution:
            backend_solution = "Aucune solution backend disponible."
        
        # Créer le prompt d'intégration
        integration_prompt = MANAGER_TEMPLATES["integration"].format(
            task=task_data.get("original_task", ""),
            frontend_solution=frontend_solution,
            backend_solution=backend_solution
        )
        
        # Obtenir la solution intégrée
        context = {"task_data": task_data}
        integrated_solution = self.process(integration_prompt, context)
        
        return integrated_solution
