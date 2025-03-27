#!/usr/bin/env python3
"""
Agent développeur backend spécialisé dans les systèmes côté serveur.
"""

from typing import Dict, Any, Optional, List

from src.agents.agent import Agent
from src.utils.prompts import BACKEND_TEMPLATES
from src.utils.logger import get_logger
import config

logger = get_logger(__name__)


class BackendDevAgent(Agent):
    """Agent développeur backend spécialisé dans les systèmes côté serveur."""
    
    def __init__(self):
        """Initialise l'agent développeur backend."""
        name = config.AGENTS["backend_dev"]["name"]
        model = config.AGENTS["backend_dev"]["model"]
        system_prompt = config.AGENTS["backend_dev"]["system_prompt"]
        
        super().__init__(name=name, role="backend_dev", model=model, system_prompt=system_prompt)
        
        logger.info(f"Agent Développeur Backend {self.name} initialisé")
    
    def design_architecture(self, feature: str, context: Dict[str, Any]) -> str:
        """Conçoit une architecture backend pour une fonctionnalité spécifique.
        
        Args:
            feature (str): Fonctionnalité pour laquelle concevoir l'architecture
            context (Dict[str, Any]): Contexte de la conception
            
        Returns:
            str: Design de l'architecture backend
        """
        # Extraire les éléments du contexte (ou utiliser des valeurs par défaut)
        functional_requirements = context.get("functional_requirements", "Exigences fonctionnelles de base")
        non_functional_requirements = context.get("non_functional_requirements", "Performance, sécurité et maintenabilité")
        
        # Créer le prompt de conception d'architecture
        architecture_prompt = BACKEND_TEMPLATES["architecture_design"].format(
            feature=feature,
            context=context.get("project_context", ""),
            functional_requirements=functional_requirements,
            non_functional_requirements=non_functional_requirements
        )
        
        # Obtenir le design d'architecture
        architecture_design = self.process(architecture_prompt, context)
        
        logger.info(f"Architecture backend conçue pour: {feature[:50]}...")
        return architecture_design
    
    def implement_api(self, api_name: str, required_endpoints: List[str], data_model: str,
                    constraints: Optional[str] = None) -> str:
        """Implémente une API backend.
        
        Args:
            api_name (str): Nom de l'API à implémenter
            required_endpoints (List[str]): Liste des endpoints requis
            data_model (str): Description du modèle de données
            constraints (str, optional): Contraintes d'implémentation
            
        Returns:
            str: Implémentation de l'API
        """
        # Valeur par défaut pour les contraintes
        if constraints is None:
            constraints = "Respecter les standards REST, assurer la sécurité et optimiser les performances."
        
        # Formater les endpoints pour le prompt
        endpoints_str = "\n".join([f"- {endpoint}" for endpoint in required_endpoints])
        
        # Créer le prompt d'implémentation d'API
        api_prompt = BACKEND_TEMPLATES["api_implementation"].format(
            api_name=api_name,
            required_endpoints=endpoints_str,
            data_model=data_model,
            constraints=constraints
        )
        
        # Contexte pour le traitement
        context = {
            "api_name": api_name,
            "required_endpoints": required_endpoints,
            "data_model": data_model,
            "constraints": constraints
        }
        
        # Obtenir l'implémentation
        implementation = self.process(api_prompt, context)
        
        logger.info(f"API backend implémentée: {api_name}")
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
        
        # Analyser la tâche pour déterminer s'il s'agit d'une conception d'architecture ou d'une implémentation d'API
        analysis_prompt = f"""
        Analysez cette tâche et déterminez s'il s'agit principalement de:
        1. Conception d'architecture backend
        2. Implémentation d'API ou de composants spécifiques
        3. Les deux
        
        TÂCHE:
        {assignment}
        
        Répondez uniquement par un chiffre : 1, 2 ou 3.
        """
        
        task_type = self.process(analysis_prompt, {"assignment": assignment})
        task_type = task_type.strip()
        
        # Exécuter la tâche en fonction de son type
        if "1" in task_type or "architecture" in task_type.lower():
            # Tâche de conception d'architecture
            feature = context.get("specific_task", "")
            
            # Extraire les exigences si possible
            extraction_prompt = f"""
            À partir de la tâche suivante, extrayez les exigences fonctionnelles et non-fonctionnelles :
            
            {assignment}
            
            Formatez votre réponse en deux sections clairement séparées :
            
            EXIGENCES FONCTIONNELLES:
            - (liste des exigences)
            
            EXIGENCES NON-FONCTIONNELLES:
            - (liste des exigences)
            """
            
            requirements = self.process(extraction_prompt, {"assignment": assignment})
            
            # Diviser les exigences
            func_reqs = ""
            non_func_reqs = ""
            
            if "EXIGENCES FONCTIONNELLES" in requirements:
                parts = requirements.split("EXIGENCES NON-FONCTIONNELLES", 1)
                func_reqs = parts[0].split("EXIGENCES FONCTIONNELLES", 1)[1].strip()
                if len(parts) > 1:
                    non_func_reqs = parts[1].strip()
            
            # Mettre à jour le contexte
            context["functional_requirements"] = func_reqs if func_reqs else "Exigences extraites de la tâche"
            context["non_functional_requirements"] = non_func_reqs if non_func_reqs else "Performance, sécurité et maintenabilité"
            
            result = self.design_architecture(feature, context)
            
        elif "2" in task_type or "api" in task_type.lower() or "implémentation" in task_type.lower():
            # Tâche d'implémentation d'API
            api_name = context.get("specific_task", "").split(":")[0] if ":" in context.get("specific_task", "") else "API"
            
            # Extraire les endpoints et le modèle de données
            extraction_prompt = f"""
            À partir de la tâche suivante, extrayez les endpoints requis et le modèle de données :
            
            {assignment}
            
            Formatez votre réponse en deux sections :
            
            ENDPOINTS:
            - (liste des endpoints)
            
            MODÈLE DE DONNÉES:
            (description du modèle)
            """
            
            api_details = self.process(extraction_prompt, {"assignment": assignment})
            
            # Extraire les endpoints
            endpoints = []
            data_model = ""
            
            if "ENDPOINTS" in api_details:
                parts = api_details.split("MODÈLE DE DONNÉES", 1)
                endpoints_text = parts[0].split("ENDPOINTS", 1)[1].strip()
                
                # Extraire chaque endpoint (lignes commençant par - ou *)
                import re
                endpoints = re.findall(r'[-*]\s*(.+)', endpoints_text)
                
                if len(parts) > 1:
                    data_model = parts[1].strip()
            
            # Valeurs par défaut si l'extraction échoue
            if not endpoints:
                endpoints = ["GET /api/{resource}", "POST /api/{resource}", "PUT /api/{resource}/{id}", "DELETE /api/{resource}/{id}"]
            
            if not data_model:
                data_model = "Modèle de données dérivé des exigences de la tâche."
            
            result = self.implement_api(api_name, endpoints, data_model, context.get("constraints"))
            
        else:
            # Tâche mixte ou indéterminée - traiter directement l'assignation
            result = self.process(f"""
            En tant que développeur backend, complétez la tâche suivante avec tous les détails nécessaires:
            
            {assignment}
            
            Fournissez une solution complète qui inclut :
            1. La conception de l'architecture backend si nécessaire
            2. L'implémentation technique avec le code nécessaire
            3. Les explications de vos choix d'architecture et d'implémentation
            4. Les interfaces d'intégration avec le frontend
            """, context)
        
        logger.info(f"Tâche backend exécutée: {context.get('specific_task', '')[:50]}...")
        return result
