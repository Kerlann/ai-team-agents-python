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
            
            # Solution simplifiée pour des résultats rapides et fiables
            if len(task_description) < 100:  # Si la tâche est courte, utilisez directement le manager
                logger.info("Tâche courte, utilisation directe du manager")
                prompt = f"""
                {task_description}
                
                Veuillez fournir une solution complète pour cette tâche. 
                Incluez:
                1. Une explication de l'approche
                2. Du code d'exemple pour le frontend (HTML/CSS/JS)
                3. Du code d'exemple pour le backend (API, base de données)
                4. Des instructions d'intégration
                
                Soyez concis mais complet.
                """
                final_solution = self.manager.process(prompt, {"task": task_description})
                
                # Finaliser le résultat
                duration = time.time() - start_time
                logger.info(f"Tâche résolue directement en {duration:.2f} secondes")
                
                return final_solution
            
            # Générer un ID pour la tâche
            import uuid
            task_id = str(uuid.uuid4())[:8]
            self.state["active_task_id"] = task_id
            
            # Analyser la tâche avec le manager
            logger.info("Étape 1: Analyse de la tâche par le manager")
            prompt = f"""
            Analysez cette tâche et fournissez une description détaillée de la solution:
            
            {task_description}
            
            Votre solution doit inclure:
            1. Une explication de l'approche
            2. Du code d'exemple pour le frontend (HTML/CSS/JS)
            3. Du code d'exemple pour le backend (API, base de données)
            4. Des instructions d'intégration
            
            Soyez détaillé et complet.
            """
            final_solution = self.manager.process(prompt, {"task": task_description})
            
            # Finaliser le résultat
            duration = time.time() - start_time
            self.state["tasks"][task_id] = {
                "description": task_description,
                "status": "completed",
                "start_time": start_time,
                "end_time": time.time(),
                "duration": duration,
                "final_solution": final_solution
            }
            
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
