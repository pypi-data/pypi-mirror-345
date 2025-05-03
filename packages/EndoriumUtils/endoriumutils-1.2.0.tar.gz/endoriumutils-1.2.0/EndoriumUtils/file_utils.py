"""
Module de gestion des fichiers pour EndoriumUtils
"""

import os
import shutil
import hashlib
import time
import json
from pathlib import Path
from contextlib import contextmanager
from typing import Union, Optional, Dict, Any, List

from EndoriumUtils.log_utils import get_logger, log_function_call

logger = get_logger("EndoriumUtils.file_utils")

@log_function_call
def ensure_dir_exists(directory: str) -> bool:
    """
    S'assure qu'un répertoire existe, le crée s'il n'existe pas
    
    Args:
        directory (str): Chemin du répertoire à vérifier/créer
        
    Returns:
        bool: True si le répertoire existe ou a été créé avec succès
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Répertoire créé: {directory}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création du répertoire {directory}: {str(e)}")
        return False

@log_function_call
def safe_read_file(file_path: str, default_content: str = "", encoding: str = "utf-8") -> str:
    """
    Lit le contenu d'un fichier de manière sécurisée
    
    Args:
        file_path (str): Chemin du fichier à lire
        default_content (str): Contenu par défaut si le fichier n'existe pas
        encoding (str): Encodage à utiliser
        
    Returns:
        str: Contenu du fichier ou contenu par défaut
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Le fichier {file_path} n'existe pas, retour du contenu par défaut")
            return default_content
            
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        return content
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {file_path}: {str(e)}")
        return default_content

@log_function_call
def safe_write_file(file_path: str, content: str, encoding: str = "utf-8", 
                    create_backup: bool = False) -> bool:
    """
    Écrit du contenu dans un fichier de manière sécurisée
    
    Args:
        file_path (str): Chemin du fichier à écrire
        content (str): Contenu à écrire
        encoding (str): Encodage à utiliser
        create_backup (bool): Si True, crée une sauvegarde avant l'écriture
        
    Returns:
        bool: True si l'écriture a réussi
    """
    try:
        # Créer le répertoire parent si nécessaire
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # Créer une sauvegarde si demandé et si le fichier existe
        if create_backup and os.path.exists(file_path):
            backup_path = f"{file_path}.bak"
            shutil.copy2(file_path, backup_path)
            logger.debug(f"Backup créé: {backup_path}")
            
        # Écriture sécurisée (écrire d'abord dans un fichier temporaire)
        temp_path = f"{file_path}.tmp"
        with open(temp_path, 'w', encoding=encoding) as f:
            f.write(content)
            
        # Remplacer le fichier original
        if os.path.exists(file_path):
            os.replace(temp_path, file_path)
        else:
            os.rename(temp_path, file_path)
            
        logger.debug(f"Fichier écrit avec succès: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier {file_path}: {str(e)}")
        return False

@log_function_call
def get_file_hash(file_path: str, algorithm: str = "sha256") -> Optional[str]:
    """
    Calcule le hash d'un fichier
    
    Args:
        file_path (str): Chemin du fichier
        algorithm (str): Algorithme de hachage (md5, sha1, sha256, etc.)
        
    Returns:
        str or None: Hash du fichier ou None en cas d'erreur
    """
    if not os.path.exists(file_path):
        logger.warning(f"Le fichier {file_path} n'existe pas")
        return None
        
    try:
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f"Erreur lors du calcul du hash pour {file_path}: {str(e)}")
        return None

@log_function_call
def is_file_newer_than(file_path: str, reference_time: Union[float, int]) -> bool:
    """
    Vérifie si un fichier est plus récent qu'une date de référence
    
    Args:
        file_path (str): Chemin du fichier à vérifier
        reference_time (float, int): Timestamp UNIX de référence
        
    Returns:
        bool: True si le fichier est plus récent, False sinon ou en cas d'erreur
    """
    try:
        if not os.path.exists(file_path):
            return False
            
        file_time = os.path.getmtime(file_path)
        return file_time > reference_time
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la date de {file_path}: {str(e)}")
        return False
