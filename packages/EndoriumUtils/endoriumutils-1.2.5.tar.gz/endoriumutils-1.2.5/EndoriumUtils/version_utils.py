"""
Module de gestion des versions pour EndoriumUtils
"""

import os
import re
import sys
from EndoriumUtils.log_utils import get_logger, log_function_call

logger = get_logger("EndoriumUtils.version_utils")

@log_function_call
def get_version_file_path(project_dir=None):
    """
    Détermine le chemin du fichier de version pour un projet
    
    Args:
        project_dir (str, optional): Répertoire du projet. Si None, utilise le répertoire courant.
        
    Returns:
        str: Chemin absolu vers le fichier version.txt
    """
    if project_dir is None:
        if getattr(sys, 'frozen', False):
            # Si on est dans un exécutable (PyInstaller)
            project_dir = os.path.dirname(sys.executable)
        else:
            # En développement, utiliser le répertoire courant
            project_dir = os.getcwd()
            
    return os.path.join(project_dir, "version.txt")

@log_function_call
def get_version(project_dir=None):
    """
    Récupère la version actuelle depuis le fichier version.txt
    
    Args:
        project_dir (str, optional): Répertoire du projet. Si None, utilise le répertoire courant.
        
    Returns:
        str: Chaîne de version (ex: "1.0.0")
        list: Liste des composants de version [major, minor, patch]
    """
    version_file = get_version_file_path(project_dir)
    
    if not os.path.exists(version_file):
        logger.warning(f"Le fichier {version_file} n'existe pas. Création avec version 1.0.0")
        write_version([1, 0, 0], project_dir)
        return "1.0.0", [1, 0, 0]
    
    with open(version_file, 'r') as f:
        version_str = f.read().strip()
    
    pattern = r'(\d+)\.(\d+)\.(\d+)'
    match = re.match(pattern, version_str)
    
    if not match:
        logger.warning(f"Format de version invalide dans {version_file}. Réinitialisation à 1.0.0")
        version = [1, 0, 0]
        version_str = "1.0.0"
        write_version(version, project_dir)
    else:
        version = [int(match.group(1)), int(match.group(2)), int(match.group(3))]
        
    return version_str, version

@log_function_call
def write_version(version, project_dir=None):
    """
    Écrit la nouvelle version dans le fichier
    
    Args:
        version (list): Liste des composants de version [major, minor, patch]
        project_dir (str, optional): Répertoire du projet. Si None, utilise le répertoire courant.
        
    Returns:
        str: Chaîne de version écrite
    """
    version_file = get_version_file_path(project_dir)
    version_str = ".".join(map(str, version))
    
    with open(version_file, 'w') as f:
        f.write(version_str)
    
    # Mettre à jour aussi version.py si existant
    version_py = os.path.join(os.path.dirname(version_file), "version.py")
    if os.path.exists(version_py):
        with open(version_py, 'w') as f:
            f.write(f'VERSION = "{version_str}"\n')
            
    logger.info(f"Version mise à jour : {version_str}")
    return version_str

@log_function_call
def increment_version(level='patch', project_dir=None):
    """
    Incrémente la version selon le niveau spécifié
    
    Args:
        level (str): Niveau d'incrémentation ('major', 'minor', 'patch')
        project_dir (str, optional): Répertoire du projet. Si None, utilise le répertoire courant.
        
    Returns:
        str: Nouvelle version après incrémentation
    """
    _, current_version = get_version(project_dir)
    major, minor, patch = current_version
    
    if level == 'patch':
        patch += 1
    elif level == 'minor':
        minor += 1
        patch = 0
    elif level == 'major':
        major += 1
        minor = 0
        patch = 0
    else:
        logger.warning(f"Niveau d'incrémentation inconnu: {level}. Utilisation de 'patch'")
        patch += 1
    
    new_version = [major, minor, patch]
    return write_version(new_version, project_dir)

@log_function_call
def set_version(version_str, project_dir=None):
    """
    Définit explicitement une version
    
    Args:
        version_str (str): Chaîne de version (ex: "1.0.0")
        project_dir (str, optional): Répertoire du projet. Si None, utilise le répertoire courant.
        
    Returns:
        str: Version définie ou None en cas d'erreur
    """
    pattern = r'(\d+)\.(\d+)\.(\d+)'
    match = re.match(pattern, version_str)
    
    if not match:
        logger.error(f"Format de version invalide: {version_str}")
        return None
        
    version = [int(match.group(1)), int(match.group(2)), int(match.group(3))]
    return write_version(version, project_dir)
