#!/usr/bin/env python3
"""
Client pour interagir avec l'API Ollama.
"""

import json
import requests
from typing import Dict, Any, Optional, List, Union
from requests.exceptions import RequestException
import time

from src.utils.logger import get_logger
import config

logger = get_logger(__name__)


class OllamaClient:
    """Client pour interagir avec l'API Ollama en local."""
    
    def __init__(self, base_url: str = config.OLLAMA_BASE_URL):
        """Initialise le client Ollama.
        
        Args:
            base_url (str): URL de base de l'API Ollama.
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, method: str = "POST", data: Optional[Dict[str, Any]] = None,
                     max_retries: int = config.MAX_RETRIES, timeout: int = config.TIMEOUT) -> Dict[str, Any]:
        """Effectue une requête à l'API Ollama.
        
        Args:
            endpoint (str): Point de terminaison API
            method (str): Méthode HTTP (GET, POST, etc.)
            data (Dict[str, Any], optional): Données à envoyer
            max_retries (int): Nombre maximum de tentatives
            timeout (int): Délai d'attente maximum en secondes
            
        Returns:
            Dict[str, Any]: Réponse de l'API
            
        Raises:
            ConnectionError: Si la connexion à l'API échoue après toutes les tentatives
        """
        url = f"{self.base_url}/{endpoint}"
        retries = 0
        
        while retries < max_retries:
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, timeout=timeout)
                elif method.upper() == "POST":
                    response = self.session.post(url, json=data, timeout=timeout)
                else:
                    raise ValueError(f"Méthode HTTP non supportée: {method}")
                
                response.raise_for_status()  # Lever une exception pour les codes d'erreur HTTP
                return response.json()
            
            except RequestException as e:
                retries += 1
                wait_time = 2 ** retries  # Backoff exponentiel
                logger.warning(f"Erreur lors de la requête à {url}: {e}. Nouvelle tentative dans {wait_time}s...")
                time.sleep(wait_time)
        
        raise ConnectionError(f"Impossible de se connecter à l'API Ollama après {max_retries} tentatives")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Liste les modèles disponibles localement.
        
        Returns:
            List[Dict[str, Any]]: Liste des modèles disponibles
        """
        response = self._make_request("api/tags", method="GET")
        return response.get("models", [])
    
    def generate(self, prompt: str, model: str = config.MODEL_NAME, system_prompt: Optional[str] = None,
               **kwargs) -> str:
        """Génère une réponse à partir d'un prompt.
        
        Args:
            prompt (str): Prompt à envoyer au modèle
            model (str): Nom du modèle à utiliser
            system_prompt (str, optional): Prompt système pour définir le contexte
            **kwargs: Paramètres additionnels pour la génération
            
        Returns:
            str: Réponse générée par le modèle
        """
        # Fusionner les paramètres par défaut avec ceux fournis
        params = config.MODEL_PARAMS.copy()
        params.update(kwargs)
        
        # Ajouter le system prompt s'il est fourni
        if system_prompt:
            params["system"] = system_prompt
        
        # Préparer les données de la requête
        data = {
            "model": model,
            "prompt": prompt,
            **params
        }
        
        # Effectuer la requête
        logger.debug(f"Envoi du prompt au modèle {model}: {prompt[:100]}...")
        response = self._make_request("api/generate", data=data)
        
        # Extraire et retourner la réponse
        generated_text = response.get("response", "")
        logger.debug(f"Réponse reçue: {generated_text[:100]}...")
        
        return generated_text
    
    def chat(self, messages: List[Dict[str, str]], model: str = config.MODEL_NAME,
            system_prompt: Optional[str] = None, **kwargs) -> str:
        """Génère une réponse de chat à partir d'une liste de messages.
        
        Args:
            messages (List[Dict[str, str]]): Liste de messages (format: [{"role": "user", "content": "..."}, ...])
            model (str): Nom du modèle à utiliser
            system_prompt (str, optional): Prompt système pour définir le contexte
            **kwargs: Paramètres additionnels pour la génération
            
        Returns:
            str: Réponse générée par le modèle
        """
        # Fusionner les paramètres par défaut avec ceux fournis
        params = config.MODEL_PARAMS.copy()
        params.update(kwargs)
        
        # Ajouter le system prompt s'il est fourni
        if system_prompt:
            params["system"] = system_prompt
        
        # Préparer les données de la requête
        data = {
            "model": model,
            "messages": messages,
            **params
        }
        
        # Effectuer la requête
        logger.debug(f"Envoi de {len(messages)} messages au modèle {model}")
        response = self._make_request("api/chat", data=data)
        
        # Extraire et retourner la réponse
        generated_text = response.get("message", {}).get("content", "")
        logger.debug(f"Réponse reçue: {generated_text[:100]}...")
        
        return generated_text
    
    def pull_model(self, model_name: str) -> bool:
        """Télécharge un modèle s'il n'est pas déjà disponible localement.
        
        Args:
            model_name (str): Nom du modèle à télécharger
            
        Returns:
            bool: True si le téléchargement réussit, False sinon
        """
        try:
            # Vérifier si le modèle est déjà disponible
            models = self.list_models()
            for model in models:
                if model.get("name") == model_name:
                    logger.info(f"Le modèle {model_name} est déjà disponible localement")
                    return True
            
            # Télécharger le modèle
            logger.info(f"Téléchargement du modèle {model_name}...")
            self._make_request("api/pull", data={"name": model_name}, timeout=3600)  # Timeout plus long pour le téléchargement
            logger.info(f"Modèle {model_name} téléchargé avec succès")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement du modèle {model_name}: {e}")
            return False
