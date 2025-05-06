"""
Database connector API for PostgreSQL and MySQL connections.
"""
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class DatabaseCredentials:
    """Handles database credentials retrieval and management."""
    
    @staticmethod
    def get_postgres_credentials() -> Dict[str, str]:
        """Get PostgreSQL connection credentials from environment variables."""
        # Default test credentials
        default_creds = {
            "host": "10.237.96.186",
            "port": "5432",
            "user": "postgres",
            "password": "8>w[:~WfUYzCL-f3F<p1",
            "database": "postgres"
        }
        
        # Try to get from environment variables
        creds = {
            "host": os.getenv("POSTGRES_HOST", default_creds["host"]),
            "port": os.getenv("POSTGRES_PORT", default_creds["port"]),
            "user": os.getenv("POSTGRES_USER", default_creds["user"]),
            "password": os.getenv("POSTGRES_PASSWORD", default_creds["password"]),
            "database": os.getenv("POSTGRES_DB", default_creds["database"])
        }
        
        return creds

    @staticmethod
    def get_mysql_credentials() -> Dict[str, str]:
        """Get MySQL connection credentials from environment variables."""
        # Default test credentials
        default_creds = {
            "host": "10.237.96.186",
            "port": "3306",
            "user": "root",
            "password": "8>w[:~WfUYzCL-f3F<p1",
            "database": "information_schema"
        }
        
        # Try to get from environment variables
        creds = {
            "host": os.getenv("MYSQL_HOST", default_creds["host"]),
            "port": os.getenv("MYSQL_PORT", default_creds["port"]),
            "user": os.getenv("MYSQL_USER", default_creds["user"]),
            "password": os.getenv("MYSQL_PASSWORD", default_creds["password"]),
            "database": os.getenv("MYSQL_DB", default_creds["database"])
        }
        
        return creds

    @staticmethod
    def build_postgres_dsn(creds: Dict[str, str]) -> str:
        """Build PostgreSQL DSN string from credentials."""
        return (f"host={creds['host']} "
                f"port={creds['port']} "
                f"user={creds['user']} "
                f"password={creds['password']} "
                f"database={creds['database']}")

    @staticmethod
    def build_mysql_dsn(creds: Dict[str, str]) -> str:
        """Build MySQL DSN string from credentials."""
        return (f"host={creds['host']} "
                f"port={creds['port']} "
                f"user={creds['user']} "
                f"password={creds['password']} "
                f"database={creds['database']}") 