"""
Script d'installation pour EndoriumUtils
"""

import os
import sys
from setuptools import setup, find_packages

# Déterminer le répertoire du setup.py
package_dir = os.path.abspath(os.path.dirname(__file__))

# Lire la description longue depuis README.md
try:
    with open(os.path.join(package_dir, "README.md"), "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    # Fallback si README.md n'est pas trouvé
    long_description = """
    EndoriumUtils - Bibliothèque d'utilitaires réutilisables pour les projets Endorium
    
    Ce module fournit des fonctionnalités communes pour la gestion des logs et des versions.
    """

# Lire la version depuis version.txt ou depuis le module
version = "1.1.4"  # Version par défaut
try:
    with open(os.path.join(package_dir, "version.txt"), "r") as f:
        version = f.read().strip()
except FileNotFoundError:
    # Si version.txt n'est pas trouvé, essayer d'importer depuis version.py
    try:
        sys.path.insert(0, package_dir)
        from version import VERSION
        version = VERSION
    except (ImportError, FileNotFoundError):
        # Garder la valeur par défaut si aucune source de version n'est trouvée
        print("Attention: Impossible de déterminer la version. Utilisation de la valeur par défaut:", version)

# Définir la configuration du package
setup(
    name="EndoriumUtils",
    version=version,
    author="Energetiq",
    author_email="energetiq@outlook.com",
    description="Utilitaires communs pour les projets Endorium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NergYR/EndoriumUtils",
    packages=find_packages(),
    license="MIT",  # Format SPDX pour remplacer le classifier License
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    keywords="logging, version management, utilities, configuration",
    project_urls={
        "Bug Reports": "https://github.com/NergYR/EndoriumUtils/issues",
        "Source": "https://github.com/NergYR/EndoriumUtils",
    },
    include_package_data=True,  # Inclure les fichiers non-Python (comme README.md)
    package_data={
        "": ["*.md", "*.txt"],  # Inclure les fichiers .md et .txt dans tous les packages
    },
    install_requires=[
        # Toutes les dépendances critiques sont dans la stdlib, rien d'obligatoire ici
    ],  # Dépendances de base
    extras_require={
        "yaml": ["pyyaml"],  # Dépendances optionnelles pour le support YAML
        "ldap": ["ldap3"],   # Dépendances optionnelles pour LDAP
    },
)
