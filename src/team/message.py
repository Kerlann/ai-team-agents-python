#!/usr/bin/env python3
"""
Système de messagerie entre agents.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

class Message:
    """Représente un message échangé entre agents."""
    
    def __init__(self, content: str, sender_id: str, sender_role: str, 
                 recipient_id: Optional[str] = None, recipient_role: Optional[str] = None,
                 message_type: str = "text", metadata: Optional[Dict[str, Any]] = None):
        """Initialise un message.
        
        Args:
            content (str): Contenu du message
            sender_id (str): ID de l'agent émetteur
            sender_role (str): Rôle de l'agent émetteur
            recipient_id (str, optional): ID de l'agent destinataire
            recipient_role (str, optional): Rôle de l'agent destinataire
            message_type (str): Type de message (text, task, result, etc.)
            metadata (Dict[str, Any], optional): Métadonnées associées au message
        """
        self.id = str(uuid.uuid4())
        self.content = content
        self.sender_id = sender_id
        self.sender_role = sender_role
        self.recipient_id = recipient_id
        self.recipient_role = recipient_role
        self.message_type = message_type
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire.
        
        Returns:
            Dict[str, Any]: Représentation du message sous forme de dictionnaire
        """
        return {
            "id": self.id,
            "content": self.content,
            "sender_id": self.sender_id,
            "sender_role": self.sender_role,
            "recipient_id": self.recipient_id,
            "recipient_role": self.recipient_role,
            "message_type": self.message_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Crée un message à partir d'un dictionnaire.
        
        Args:
            data (Dict[str, Any]): Données du message
            
        Returns:
            Message: Instance de message
        """
        message = cls(
            content=data["content"],
            sender_id=data["sender_id"],
            sender_role=data["sender_role"],
            recipient_id=data.get("recipient_id"),
            recipient_role=data.get("recipient_role"),
            message_type=data.get("message_type", "text"),
            metadata=data.get("metadata", {})
        )
        message.id = data["id"]
        message.timestamp = data["timestamp"]
        return message


class MessageBus:
    """Gestionnaire de messages qui facilite la communication entre agents."""
    
    def __init__(self):
        """Initialise le bus de messages."""
        self.messages: List[Message] = []
        self.subscribers: Dict[str, List[callable]] = {}
    
    def send_message(self, message: Message) -> str:
        """Envoie un message dans le bus.
        
        Args:
            message (Message): Message à envoyer
            
        Returns:
            str: ID du message envoyé
        """
        # Ajouter le message à l'historique
        self.messages.append(message)
        
        # Notifier les abonnés
        self._notify_subscribers(message)
        
        return message.id
    
    def subscribe(self, message_filter: Dict[str, Any], callback: callable) -> None:
        """Abonne une fonction de rappel pour recevoir des messages filtrés.
        
        Args:
            message_filter (Dict[str, Any]): Critères de filtrage des messages
            callback (callable): Fonction à appeler lorsqu'un message correspond au filtre
        """
        filter_key = str(message_filter)  # Utiliser une représentation du filtre comme clé
        
        if filter_key not in self.subscribers:
            self.subscribers[filter_key] = []
        
        self.subscribers[filter_key].append({
            "filter": message_filter,
            "callback": callback
        })
    
    def unsubscribe(self, message_filter: Dict[str, Any], callback: callable) -> bool:
        """Désabonne une fonction de rappel.
        
        Args:
            message_filter (Dict[str, Any]): Critères de filtrage utilisés lors de l'abonnement
            callback (callable): Fonction à désabonner
            
        Returns:
            bool: True si le désabonnement réussit, False sinon
        """
        filter_key = str(message_filter)
        
        if filter_key not in self.subscribers:
            return False
        
        # Rechercher l'abonnement correspondant
        for i, subscriber in enumerate(self.subscribers[filter_key]):
            if subscriber["callback"] == callback:
                # Supprimer l'abonnement
                self.subscribers[filter_key].pop(i)
                
                # Supprimer la clé si aucun abonné ne reste
                if not self.subscribers[filter_key]:
                    del self.subscribers[filter_key]
                
                return True
        
        return False
    
    def get_messages(self, filters: Optional[Dict[str, Any]] = None) -> List[Message]:
        """Récupère les messages correspondant aux filtres.
        
        Args:
            filters (Dict[str, Any], optional): Critères de filtrage
            
        Returns:
            List[Message]: Messages filtrés
        """
        if not filters:
            return self.messages.copy()
        
        filtered_messages = []
        
        for message in self.messages:
            match = True
            
            for key, value in filters.items():
                if hasattr(message, key):
                    if getattr(message, key) != value:
                        match = False
                        break
                elif key in message.metadata:
                    if message.metadata[key] != value:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                filtered_messages.append(message)
        
        return filtered_messages
    
    def _notify_subscribers(self, message: Message) -> None:
        """Notifie les abonnés correspondant au message.
        
        Args:
            message (Message): Message à notifier
        """
        for filter_key, subscribers in self.subscribers.items():
            for subscriber in subscribers:
                match = True
                
                for key, value in subscriber["filter"].items():
                    if hasattr(message, key):
                        if getattr(message, key) != value:
                            match = False
                            break
                    elif key in message.metadata:
                        if message.metadata[key] != value:
                            match = False
                            break
                    else:
                        match = False
                        break
                
                if match:
                    # Appeler la fonction de rappel avec le message
                    subscriber["callback"](message)
