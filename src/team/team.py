#!/usr/bin/env python3
"""
Classe pour gérer une équipe d'agents IA.
"""

from typing import Dict, Any, Optional, List
import time
from datetime import datetime
import traceback

from src.agents.manager import ManagerAgent
from src.agents.frontend_dev import FrontendDevAgent
from src.agents.backend_dev import BackendDevAgent
from src.team.message import MessageBus, Message
from src.utils.logger import get_logger
import config

logger = get_logger(__name__)


class AITeam:
    """Équipe d'agents IA collaborant pour résoudre des problèmes de développement."""
    
    def __init__(self):
        """Initialise l'équipe d'agents IA."""
        # Créer les agents
        self.manager = ManagerAgent()
        self.frontend_dev = FrontendDevAgent()
        self.backend_dev = BackendDevAgent()
        
        # Système de messagerie
        self.message_bus = MessageBus()
        
        # État interne
        self.state = {
            "tasks": {},  # Tâches en cours de traitement
            "results": {},  # Résultats des tâches
            "active_task_id": None,  # ID de la tâche active
        }
        
        logger.info("Équipe d'agents IA initialisée")
    
    def solve_task(self, task_description: str, timeout: int = config.DEFAULT_TASK_TIMEOUT) -> str:
        """Résout une tâche complexe en utilisant l'équipe d'agents.
        
        Args:
            task_description (str): Description de la tâche à résoudre
            timeout (int): Délai maximum d'exécution en secondes
            
        Returns:
            str: Solution finale pour la tâche
        """
        try:
            logger.info(f"Résolution de tâche: {task_description[:100]}...")
            start_time = time.time()
            
            # Générer un ID pour la tâche
            import uuid
            task_id = str(uuid.uuid4())[:8]
            self.state["active_task_id"] = task_id
            
            # Analyser la tâche avec le manager
            logger.info("Étape 1: Analyse de la tâche par le manager")
            task_analysis = self.manager.analyze_task(task_description)
            self.state["tasks"][task_id] = {
                "description": task_description,
                "analysis": task_analysis,
                "frontend_results": [],
                "backend_results": [],
                "status": "analyzed",
                "start_time": start_time
            }
            
            # Traiter les sous-tâches frontend et backend
            frontend_tasks = task_analysis.get("frontend_tasks", [])
            backend_tasks = task_analysis.get("backend_tasks", [])
            
            logger.info(f"Étape 2: Traitement de {len(frontend_tasks)} tâches frontend et {len(backend_tasks)} tâches backend")
            
            # Exécuter les tâches frontend
            for i, task in enumerate(frontend_tasks):
                # Vérifier le timeout
                if time.time() - start_time > timeout:
                    logger.warning(f"Timeout atteint après {i} tâches frontend")
                    break
                    
                logger.info(f"Tâche frontend {i+1}/{len(frontend_tasks)}: {task[:50]}...")
                
                # Créer l'assignation de tâche
                task_assignment = self.manager.create_task_assignment(task_analysis, "frontend_dev", i)
                
                # Exécuter la tâche
                frontend_solution = self.frontend_dev.execute_task(task_assignment)
                
                # Réviser le travail
                review = self.manager.review_work(task_analysis, "frontend_dev", frontend_solution)
                
                # Enregistrer le résultat
                self.state["tasks"][task_id]["frontend_results"].append({
                    "task": task,
                    "solution": frontend_solution,
                    "review": review,
                    "approved": review.get("approved", False)
                })
            
            # Exécuter les tâches backend
            for i, task in enumerate(backend_tasks):
                # Vérifier le timeout
                if time.time() - start_time > timeout:
                    logger.warning(f"Timeout atteint après {i} tâches backend")
                    break
                    
                logger.info(f"Tâche backend {i+1}/{len(backend_tasks)}: {task[:50]}...")
                
                # Créer l'assignation de tâche
                task_assignment = self.manager.create_task_assignment(task_analysis, "backend_dev", i)
                
                # Exécuter la tâche
                backend_solution = self.backend_dev.execute_task(task_assignment)
                
                # Réviser le travail
                review = self.manager.review_work(task_analysis, "backend_dev", backend_solution)
                
                # Enregistrer le résultat
                self.state["tasks"][task_id]["backend_results"].append({
                    "task": task,
                    "solution": backend_solution,
                    "review": review,
                    "approved": review.get("approved", False)
                })
            
            # Intégrer les solutions
            logger.info("Étape 3: Intégration des solutions par le manager")
            
            # Gérer le cas où il n'y a pas de tâches
            if not frontend_tasks and not backend_tasks:
                # Demander directement au manager de résoudre la tâche complète
                logger.info("Aucune sous-tâche trouvée, demandant au manager de résoudre directement")
                direct_prompt = f"""
                Aucune sous-tâche n'a été identifiée pour cette tâche. 
                Veuillez fournir une solution complète pour la tâche suivante:
                
                {task_description}
                
                Incluez à la fois les aspects frontend et backend dans votre solution. 
                Fournissez du code exemplaire et des explications détaillées.
                """
                final_solution = self.manager.process(direct_prompt, {"task": task_description})
            else:
                # Extraire les solutions frontend et backend approuvées
                frontend_solutions = "\n\n".join([res["solution"] for res in self.state["tasks"][task_id]["frontend_results"] if res.get("approved", False)])
                backend_solutions = "\n\n".join([res["solution"] for res in self.state["tasks"][task_id]["backend_results"] if res.get("approved", False)])
                
                # Si aucune solution n'est approuvée, utiliser toutes les solutions
                if not frontend_solutions:
                    frontend_solutions = "\n\n".join([res["solution"] for res in self.state["tasks"][task_id]["frontend_results"]])
                if not backend_solutions:
                    backend_solutions = "\n\n".join([res["solution"] for res in self.state["tasks"][task_id]["backend_results"]])
                
                # Intégrer les solutions
                final_solution = self.manager.integrate_solutions(
                    task_analysis,
                    frontend_solutions,
                    backend_solutions
                )
            
            # Finaliser le résultat
            duration = time.time() - start_time
            self.state["tasks"][task_id]["status"] = "completed"
            self.state["tasks"][task_id]["end_time"] = time.time()
            self.state["tasks"][task_id]["duration"] = duration
            self.state["tasks"][task_id]["final_solution"] = final_solution
            
            # Enregistrer le résultat final
            self.state["results"][task_id] = {
                "task": task_description,
                "solution": final_solution,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Tâche résolue en {duration:.2f} secondes")
            return final_solution
        
        except Exception as e:
            error_msg = f"Erreur lors de la résolution de la tâche: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return f"""
            ERREUR LORS DE LA RÉSOLUTION DE LA TÂCHE
            
            {error_msg}
            
            Veuillez vérifier les journaux pour plus de détails.
            """
    
    def get_agent(self, role: str):
        """Récupère un agent par son rôle.
        
        Args:
            role (str): Rôle de l'agent ("manager", "frontend_dev", "backend_dev")
            
        Returns:
            Agent: Instance de l'agent demandé ou None si non trouvé
        """
        if role == "manager":
            return self.manager
        elif role == "frontend_dev":
            return self.frontend_dev
        elif role == "backend_dev":
            return self.backend_dev
        else:
            return None
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Récupère le statut d'une tâche.
        
        Args:
            task_id (str): ID de la tâche
            
        Returns:
            Dict[str, Any]: Statut de la tâche ou None si non trouvée
        """
        return self.state["tasks"].get(task_id)
    
    def get_active_task(self) -> Dict[str, Any]:
        """Récupère la tâche active en cours.
        
        Returns:
            Dict[str, Any]: Tâche active ou None si aucune
        """
        active_id = self.state["active_task_id"]
        if active_id:
            return self.state["tasks"].get(active_id)
        return None
