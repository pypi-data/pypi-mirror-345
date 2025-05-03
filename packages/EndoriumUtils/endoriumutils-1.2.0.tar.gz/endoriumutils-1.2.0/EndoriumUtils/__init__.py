"""
EndoriumUtils - Bibliothèque d'utilitaires réutilisables pour les projets Endorium

Ce module fournit des fonctionnalités communes qui peuvent être utilisées 
dans différents projets, principalement:
- Gestion des logs (configuration, rotation, purge)
- Gestion des versions (lecture, incrémentation)
- Gestion des fichiers (lecture/écriture sécurisée)
- Gestion des configurations (chargement/sauvegarde)
"""

from EndoriumUtils.log_utils import (
    setup_logger,
    get_logger,
    log_function_call,
    log_performance,
    purge_old_logs,
    set_log_level,
    get_log_file_paths,
    log_exceptions,
)
from EndoriumUtils.version_utils import (
    get_version,
    increment_version,
    set_version,
)
from EndoriumUtils.file_utils import (
    safe_read_file,
    safe_write_file,
    ensure_dir_exists,
    get_file_hash,
    is_file_newer_than,
)
from EndoriumUtils.config_utils import (
    load_config,
    save_config,
    get_config_value,
    set_config_value,
)

__all__ = [
    "setup_logger",
    "get_logger",
    "log_function_call",
    "log_performance",
    "purge_old_logs",
    "set_log_level",
    "get_log_file_paths",
    "log_exceptions",
    "get_version",
    "increment_version",
    "set_version",
    "safe_read_file",
    "safe_write_file",
    "ensure_dir_exists",
    "get_file_hash",
    "is_file_newer_than",
    "load_config",
    "save_config",
    "get_config_value",
    "set_config_value",
]

__version__ = "1.1.4"
