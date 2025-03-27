#!/usr/bin/env python3
"""
Module de journalisation pour le système d'agents IA.
"""

import logging
import sys
from pathlib import Path


def setup_logger(level, log_format, log_file=None):
    """Configure le système de journalisation.
    
    Args:
        level (str): Niveau de journalisation (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format (str): Format des messages de journal
        log_file (str, optional): Chemin du fichier de journal. Si None, les journaux sont envoyés à stdout.
    """
    # Convertir le niveau de string à constante de logging
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Niveau de journalisation invalide : {level}")
    
    # Configuration de base
    handlers = []
    
    # Handler de console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)
    
    # Handler de fichier (si spécifié)
    if log_file:
        # Créer le dossier parent si nécessaire
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    # Configuration générale
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        force=True  # Remplacer la configuration existante
    )
    
    # Retourner le logger racine configuré
    return logging.getLogger()


def get_logger(name):
    """Obtient un logger nommé.
    
    Args:
        name (str): Nom du logger
        
    Returns:
        logging.Logger: Instance de logger configurée
    """
    return logging.getLogger(name)
