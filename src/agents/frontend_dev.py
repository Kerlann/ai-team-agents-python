#!/usr/bin/env python3
"""
Agent développeur frontend spécialisé dans les interfaces utilisateur.
"""

from typing import Dict, Any, Optional

from src.agents.agent import Agent
from src.utils.prompts import FRONTEND_TEMPLATES
from src.utils.logger import get_logger
import config

logger = get_logger(__name__)


class FrontendDevAgent(Agent):
    """Agent développeur frontend spécialisé dans la création d'interfaces utilisateur."""
    
    def __init__(self):
        """Initialise l'agent développeur frontend."""
        name = config.AGENTS["frontend_dev"]["name"]
        model = config.AGENTS["frontend_dev"]["model"]
        system_prompt = config.AGENTS["frontend_dev"]["system_prompt"]
        
        super().__init__(name=name, role="frontend_dev", model=model, system_prompt=system_prompt)
        
        logger.info(f"Agent Développeur Frontend {self.name} initialisé")
    
    def design_ui(self, feature: str, context: Dict[str, Any]) -> str:
        """Conçoit une interface utilisateur pour une fonctionnalité spécifique.
        
        Args:
            feature (str): Fonctionnalité pour laquelle concevoir l'interface
            context (Dict[str, Any]): Contexte de la conception
            
        Returns:
            str: Design de l'interface utilisateur
        """
        # Extraire les éléments du contexte (ou utiliser des valeurs par défaut)
        target_users = context.get("target_users", "Utilisateurs généraux de l'application")
        required_features = context.get("required_features", "Fonctionnalités de base nécessaires")
        
        # Créer le prompt de conception
        design_prompt = FRONTEND_TEMPLATES["ui_design"].format(
            feature=feature,
            context=context.get("project_context", ""),
            target_users=target_users,
            required_features=required_features
        )
        
        # Obtenir le design
        ui_design = self.process(design_prompt, context)
        
        logger.info(f"Design UI créé pour la fonctionnalité: {feature[:50]}...")
        return ui_design
    
    def implement_component(self, component_name: str, specifications: str, 
                          backend_integration: Optional[str] = None,
                          recommended_technologies: Optional[str] = None) -> str:
        """Implémente un composant frontend.
        
        Args:
            component_name (str): Nom du composant à implémenter
            specifications (str): Spécifications détaillées du composant
            backend_integration (str, optional): Détails sur l'intégration avec le backend
            recommended_technologies (str, optional): Technologies recommandées
            
        Returns:
            str: Implémentation du composant
        """
        # Valeurs par défaut
        if backend_integration is None:
            backend_integration = "Utiliser les API REST standards pour l'intégration."
        
        if recommended_technologies is None:
            recommended_technologies = "HTML, CSS, JavaScript, et un framework moderne comme React, Vue ou Angular."
        
        # Créer le prompt d'implémentation
        implementation_prompt = FRONTEND_TEMPLATES["component_implementation"].format(
            component_name=component_name,
            specifications=specifications,
            backend_integration=backend_integration,
            recommended_technologies=recommended_technologies
        )
        
        # Contexte pour le traitement
        context = {
            "component_name": component_name,
            "specifications": specifications,
            "backend_integration": backend_integration,
            "recommended_technologies": recommended_technologies
        }
        
        # Obtenir l'implémentation
        implementation = self.process(implementation_prompt, context)
        
        logger.info(f"Composant frontend implémenté: {component_name}")
        return implementation
    
    def execute_task(self, task_assignment: Dict[str, Any]) -> str:
        """Exécute une tâche assignée par le manager.
        
        Args:
            task_assignment (Dict[str, Any]): Assignation de tâche du manager
            
        Returns:
            str: Solution produite pour la tâche
        """
        # Extraire l'assignation et le contexte
        assignment = task_assignment.get("assignment", "")
        context = task_assignment.get("context", {})
        
        # Analyser la tâche pour déterminer s'il s'agit d'une conception UI ou d'une implémentation
        analysis_prompt = f"""
        Analysez cette tâche et déterminez s'il s'agit principalement de:
        1. Conception d'interface utilisateur (UI/UX design)
        2. Implémentation d'un composant ou d'une fonctionnalité spécifique
        3. Les deux
        
        TÂCHE:
        {assignment}
        
        Répondez uniquement par un chiffre : 1, 2 ou 3.
        """
        
        task_type = self.process(analysis_prompt, {"assignment": assignment})
        task_type = task_type.strip()
        
        # Exécuter la tâche en fonction de son type
        if "1" in task_type or "conception" in task_type.lower():
            # Tâche de conception UI
            feature = context.get("specific_task", "")
            result = self.design_ui(feature, context)
        elif "2" in task_type or "implémentation" in task_type.lower():
            # Tâche d'implémentation
            component_name = context.get("specific_task", "").split(":")[0] if ":" in context.get("specific_task", "") else "Composant"
            specifications = context.get("specific_task", "")
            backend_integration = context.get("interfaces", "")
            result = self.implement_component(component_name, specifications, backend_integration)
        else:
            # Tâche mixte ou indéterminée - traiter directement l'assignation
            result = self.process(f"""En tant que développeur frontend, complétez la tâche suivante avec tous les détails nécessaires:
            
            {assignment}
            
            Fournissez une solution complète qui inclut :
            1. La conception de l'interface utilisateur
            2. L'implémentation technique avec le code nécessaire
            3. Les explications de vos choix de design et d'implémentation
            4. Les instructions d'intégration avec le backend
            """, context)
        
        logger.info(f"Tâche frontend exécutée: {context.get('specific_task', '')[:50]}...")
        return result
