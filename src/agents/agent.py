#!/usr/bin/env python3
"""
Classe de base pour les agents IA.
"""

from typing import Dict, Any, List, Optional
import json
import time
from datetime import datetime
import uuid

from src.llm.ollama_client import OllamaClient
from src.utils.logger import get_logger
import config

logger = get_logger(__name__)


class Agent:
    """Classe de base pour tous les agents IA."""
    
    def __init__(self, name: str, role: str, model: str = config.MODEL_NAME, 
                 system_prompt: Optional[str] = None):
        """Initialise un agent.
        
        Args:
            name (str): Nom de l'agent
            role (str): Rôle de l'agent (manager, frontend_dev, backend_dev)
            model (str): Modèle de langage à utiliser
            system_prompt (str, optional): Prompt système à utiliser pour toutes les interactions
        """
        self.name = name
        self.role = role
        self.model = model
        self.system_prompt = system_prompt
        self.id = str(uuid.uuid4())[:8]  # Identifiant unique court pour l'agent
        
        # Client pour interagir avec Ollama
        self.llm_client = OllamaClient()
        
        # Historique des conversations
        self.conversation_history = []
        
        logger.info(f"Agent {self.name} ({self.role}) initialisé avec ID {self.id}")
    
    def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Traite un message et génère une réponse.
        
        Args:
            message (str): Message à traiter
            context (Dict[str, Any], optional): Contexte supplémentaire pour le traitement
            
        Returns:
            str: Réponse générée par l'agent
        """
        # Préparer le contexte
        full_context = self._prepare_context(context)
        
        # Construire le prompt complet
        prompt = self._build_prompt(message, full_context)
        
        # Générer la réponse via le modèle de langage
        start_time = time.time()
        response = self.llm_client.generate(prompt, model=self.model, system_prompt=self.system_prompt)
        processing_time = time.time() - start_time
        
        # Enregistrer l'interaction dans l'historique
        self._update_history(message, response, context)
        
        logger.info(f"Agent {self.name} a traité un message en {processing_time:.2f}s")
        return response
    
    def chat(self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None) -> str:
        """Traite une conversation et génère une réponse.
        
        Args:
            messages (List[Dict[str, str]]): Liste de messages au format [{"role": "user", "content": "..."}]
            context (Dict[str, Any], optional): Contexte supplémentaire pour le traitement
            
        Returns:
            str: Réponse générée par l'agent
        """
        # Préparer le contexte
        full_context = self._prepare_context(context)
        
        # Ajouter le contexte au premier message si nécessaire
        if full_context and messages:
            # Trouver le premier message utilisateur
            for i, msg in enumerate(messages):
                if msg.get("role") == "user":
                    # Ajouter le contexte au message
                    context_str = f"\n\nCONTEXTE:\n{json.dumps(full_context, indent=2, ensure_ascii=False)}"
                    messages[i]["content"] = msg["content"] + context_str
                    break
        
        # Générer la réponse via le modèle de langage
        start_time = time.time()
        response = self.llm_client.chat(messages, model=self.model, system_prompt=self.system_prompt)
        processing_time = time.time() - start_time
        
        # Enregistrer l'interaction dans l'historique
        self._update_history(messages[-1]["content"] if messages else "", response, context)
        
        logger.info(f"Agent {self.name} a traité une conversation en {processing_time:.2f}s")
        return response
    
    def _prepare_context(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prépare le contexte complet pour le traitement.
        
        Args:
            context (Dict[str, Any], optional): Contexte supplémentaire fourni
            
        Returns:
            Dict[str, Any]: Contexte complet
        """
        full_context = {
            "agent": {
                "name": self.name,
                "role": self.role,
                "id": self.id
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if context:
            full_context.update(context)
            
        return full_context
    
    def _build_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """Construit le prompt complet avec le message et le contexte.
        
        Args:
            message (str): Message principal
            context (Dict[str, Any]): Contexte
            
        Returns:
            str: Prompt complet
        """
        # Construire le prompt avec le contexte
        context_str = json.dumps(context, indent=2, ensure_ascii=False)
        prompt = f"{message}\n\nCONTEXTE:\n{context_str}"
        
        return prompt
    
    def _update_history(self, message: str, response: str, context: Optional[Dict[str, Any]] = None):
        """Met à jour l'historique des conversations.
        
        Args:
            message (str): Message reçu
            response (str): Réponse générée
            context (Dict[str, Any], optional): Contexte associé
        """
        # Créer l'entrée d'historique
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "context": context
        }
        
        # Ajouter à l'historique
        self.conversation_history.append(history_entry)
        
        # Limiter la taille de l'historique
        max_history = config.HISTORY_CONFIG.get("max_messages", 50)
        if len(self.conversation_history) > max_history:
            self.conversation_history = self.conversation_history[-max_history:]
        
        # Sauvegarder l'historique si configuré
        if config.HISTORY_CONFIG.get("save_history", False):
            self._save_history()
    
    def _save_history(self):
        """Sauvegarde l'historique des conversations dans un fichier."""
        try:
            history_dir = config.HISTORY_CONFIG.get("history_dir", "conversation_history")
            filename = f"{history_dir}/{self.role}_{self.id}_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Historique de l'agent {self.name} sauvegardé dans {filename}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'historique: {e}")
