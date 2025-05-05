"""
Module d'authentification flexible pour EndoriumUtils

Supporte :
- Authentification simple (plain)
- Authentification sécurisée (hash)
- Authentification base de données (sqlite, sql)
- Authentification LDAP/AD/Azure
- Authentification SSO (Google, Microsoft, Apple) [placeholders]
"""

import hashlib
import sqlite3
from typing import Optional, Dict, Any

try:
    import ldap3
except ImportError:
    ldap3 = None

from EndoriumUtils.log_utils import get_logger, log_function_call

logger = get_logger("EndoriumUtils.auth_utils")

class BaseAuthenticator:
    def authenticate(self, username: str, password: str) -> bool:
        raise NotImplementedError

# --- Authentification simple (plain) ---
class PlainAuthenticator(BaseAuthenticator):
    def __init__(self, users: Dict[str, str]):
        self.users = users

    @log_function_call
    def authenticate(self, username: str, password: str) -> bool:
        return self.users.get(username) == password

# --- Authentification sécurisée (hash) ---
class SecureAuthenticator(BaseAuthenticator):
    def __init__(self, users: Dict[str, str], hash_algo: str = "sha256"):
        self.users = users
        self.hash_algo = hash_algo

    @log_function_call
    def authenticate(self, username: str, password: str) -> bool:
        hashed = hashlib.new(self.hash_algo, password.encode()).hexdigest()
        return self.users.get(username) == hashed

# --- Authentification base de données SQLite ---
class SQLiteAuthenticator(BaseAuthenticator):
    def __init__(self, db_path: str):
        self.db_path = db_path

    @log_function_call
    def authenticate(self, username: str, password: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0] == password
        return False

# --- Authentification LDAP/AD/Azure ---
class LDAPAuthenticator(BaseAuthenticator):
    def __init__(self, server_uri: str, base_dn: str, user_template: str):
        if ldap3 is None:
            raise ImportError("ldap3 requis pour LDAPAuthenticator")
        self.server_uri = server_uri
        self.base_dn = base_dn
        self.user_template = user_template

    @log_function_call
    def authenticate(self, username: str, password: str) -> bool:
        from ldap3 import Server, Connection, ALL
        server = Server(self.server_uri, get_info=ALL)
        user_dn = self.user_template.format(username=username, base_dn=self.base_dn)
        try:
            conn = Connection(server, user=user_dn, password=password, auto_bind=True)
            conn.unbind()
            return True
        except Exception as e:
            logger.warning(f"LDAP auth failed: {e}")
            return False

# --- Authentification SSO (OAuth2) [placeholders] ---
class SSOAuthenticator(BaseAuthenticator):
    def __init__(self, provider: str, client_id: str, client_secret: str, redirect_uri: str):
        self.provider = provider
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @log_function_call
    def authenticate(self, username: str, password: str) -> bool:
        logger.warning("SSOAuthenticator: implémentation OAuth2 requise (placeholder)")
        return False

# --- Factory pour choisir l'authentificateur ---
@log_function_call
def get_authenticator(method: str, **kwargs) -> BaseAuthenticator:
    """
    Retourne un authentificateur selon la méthode choisie.
    method: 'plain', 'secure', 'sqlite', 'ldap', 'sso'
    kwargs: paramètres spécifiques à chaque backend
    """
    if method == "plain":
        return PlainAuthenticator(kwargs.get("users", {}))
    elif method == "secure":
        return SecureAuthenticator(kwargs.get("users", {}), kwargs.get("hash_algo", "sha256"))
    elif method == "sqlite":
        return SQLiteAuthenticator(kwargs["db_path"])
    elif method == "ldap":
        return LDAPAuthenticator(
            kwargs["server_uri"],
            kwargs["base_dn"],
            kwargs.get("user_template", "uid={username},{base_dn}")
        )
    elif method == "sso":
        return SSOAuthenticator(
            kwargs["provider"],
            kwargs["client_id"],
            kwargs["client_secret"],
            kwargs["redirect_uri"]
        )
    else:
        raise ValueError(f"Méthode d'authentification inconnue: {method}")
