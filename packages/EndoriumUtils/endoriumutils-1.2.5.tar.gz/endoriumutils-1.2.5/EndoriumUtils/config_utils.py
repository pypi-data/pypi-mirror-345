"""
Module de gestion des configurations pour EndoriumUtils
"""

import os
import sys
import json
from typing import Dict, Any, Optional, Union
import tempfile
import base64
import hashlib
import secrets

from EndoriumUtils.log_utils import get_logger, log_function_call
from EndoriumUtils.file_utils import safe_read_file, safe_write_file

logger = get_logger("EndoriumUtils.config_utils")

@log_function_call
def load_config(config_path: str, default_config: Optional[Dict] = None, 
                file_format: str = "auto") -> Dict[str, Any]:
    """
    Charge une configuration depuis un fichier
    
    Args:
        config_path (str): Chemin du fichier de configuration
        default_config (dict, optional): Configuration par défaut à utiliser si le fichier n'existe pas
        file_format (str): Format du fichier ('json', 'yaml', 'auto' pour détection automatique)
        
    Returns:
        dict: Configuration chargée ou configuration par défaut
    """
    if default_config is None:
        default_config = {}
        
    # Détection du format si 'auto'
    if file_format == "auto":
        _, ext = os.path.splitext(config_path)
        if ext.lower() in ('.yml', '.yaml'):
            file_format = "yaml"
        elif ext.lower() == '.json':
            file_format = "json"
        else:
            file_format = "json"  # Format par défaut
            
    try:
        if not os.path.exists(config_path):
            logger.warning(f"Fichier de configuration {config_path} non trouvé, utilisation des valeurs par défaut")
            return default_config.copy()
            
        content = safe_read_file(config_path)
        if not content:
            return default_config.copy()
            
        if file_format == "json":
            config = json.loads(content)
        elif file_format == "yaml":
            try:
                import yaml  # Import conditionnel
                config = yaml.safe_load(content)
            except ImportError:
                logger.error("Module yaml non disponible. Installez-le avec 'pip install pyyaml'")
                return default_config.copy()
        else:
            logger.error(f"Format de configuration non supporté: {file_format}")
            return default_config.copy()
            
        # Fusionner avec la configuration par défaut pour garantir la structure
        merged_config = default_config.copy()
        _deep_update(merged_config, config)
        
        return merged_config
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration {config_path}: {str(e)}")
        return default_config.copy()

@log_function_call
def save_config(config: Dict[str, Any], config_path: str, 
                file_format: str = "auto", indent: int = 2) -> bool:
    """
    Enregistre une configuration dans un fichier
    
    Args:
        config (dict): Configuration à enregistrer
        config_path (str): Chemin du fichier de destination
        file_format (str): Format du fichier ('json', 'yaml', 'auto' pour détection automatique)
        indent (int): Indentation pour le formatage
        
    Returns:
        bool: True si l'enregistrement a réussi
    """
    # Détection du format si 'auto'
    if file_format == "auto":
        _, ext = os.path.splitext(config_path)
        if ext.lower() in ('.yml', '.yaml'):
            file_format = "yaml"
        elif ext.lower() == '.json':
            file_format = "json"
        else:
            file_format = "json"  # Format par défaut
    
    try:
        if file_format == "json":
            content = json.dumps(config, indent=indent, ensure_ascii=False)
        elif file_format == "yaml":
            try:
                import yaml  # Import conditionnel
                content = yaml.safe_dump(config, indent=indent, allow_unicode=True)
            except ImportError:
                logger.error("Module yaml non disponible. Installez-le avec 'pip install pyyaml'")
                return False
        else:
            logger.error(f"Format de configuration non supporté: {file_format}")
            return False
            
        return safe_write_file(config_path, content, create_backup=True)
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de la configuration {config_path}: {str(e)}")
        return False

@log_function_call
def get_config_value(config: Dict[str, Any], key_path: str, default_value: Any = None) -> Any:
    """
    Récupère une valeur dans une configuration en utilisant une notation en points
    
    Args:
        config (dict): Configuration dans laquelle chercher
        key_path (str): Chemin de la clé (ex: "section.sous_section.valeur")
        default_value (any): Valeur par défaut si la clé n'est pas trouvée
        
    Returns:
        any: Valeur trouvée ou valeur par défaut
    """
    parts = key_path.split('.')
    current = config
    
    try:
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return default_value
            current = current[part]
        return current
    except Exception:
        return default_value

@log_function_call
def set_config_value(config: Dict[str, Any], key_path: str, value: Any) -> Dict[str, Any]:
    """
    Définit une valeur dans une configuration en utilisant une notation en points
    
    Args:
        config (dict): Configuration à modifier
        key_path (str): Chemin de la clé (ex: "section.sous_section.valeur")
        value (any): Valeur à définir
        
    Returns:
        dict: Configuration modifiée
    """
    parts = key_path.split('.')
    current = config
    
    # Parcourir la hiérarchie sauf le dernier élément
    for i, part in enumerate(parts[:-1]):
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
        
    # Définir la valeur pour le dernier élément
    current[parts[-1]] = value
    return config

def _deep_update(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """Mise à jour profonde d'un dictionnaire avec un autre"""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update(target[key], value)
        else:
            target[key] = value
    return target

def set_password(config: Dict[str, Any], key_path: str, password: str, iterations: int = 100_000) -> Dict[str, Any]:
    """
    Stocke un mot de passe de façon sécurisée (hash PBKDF2 + sel) dans la configuration.
    Le résultat est une chaîne base64 contenant le sel et le hash.
    Args:
        config (dict): Configuration à modifier
        key_path (str): Chemin de la clé (ex: "auth.admin_password")
        password (str): Mot de passe en clair à stocker
        iterations (int): Nombre d'itérations PBKDF2 (défaut: 100_000)
    Returns:
        dict: Configuration modifiée
    """
    salt = secrets.token_bytes(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    data = {
        "salt": base64.b64encode(salt).decode("utf-8"),
        "hash": base64.b64encode(hash_bytes).decode("utf-8"),
        "iterations": iterations,
        "algo": "pbkdf2_sha256"
    }
    set_config_value(config, key_path, data)
    return config

def verify_password(config: Dict[str, Any], key_path: str, password: str) -> bool:
    """
    Vérifie un mot de passe par rapport à la valeur stockée dans la configuration.
    Args:
        config (dict): Configuration à lire
        key_path (str): Chemin de la clé (ex: "auth.admin_password")
        password (str): Mot de passe à vérifier
    Returns:
        bool: True si le mot de passe est correct, False sinon
    """
    data = get_config_value(config, key_path)
    if not isinstance(data, dict):
        return False
    try:
        salt = base64.b64decode(data["salt"])
        hash_stored = base64.b64decode(data["hash"])
        iterations = int(data.get("iterations", 100_000))
        algo = data.get("algo", "pbkdf2_sha256")
        if algo != "pbkdf2_sha256":
            logger.error(f"Algorithme non supporté: {algo}")
            return False
        hash_test = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return secrets.compare_digest(hash_stored, hash_test)
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du mot de passe: {str(e)}")
        return False
