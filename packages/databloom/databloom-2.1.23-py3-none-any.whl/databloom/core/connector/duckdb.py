"""
DuckDB connector implementation.
"""
import os
import logging
from typing import Optional, Dict, Any
import duckdb
from sqlalchemy import create_engine, Engine
from databloom.api.credentials import CredentialsManager

logger = logging.getLogger(__name__)

class DuckDBConnector:
    """DuckDB connector for managing connections and queries."""

    def __init__(self):
        """Initialize DuckDB connector."""
        self._credentials_manager = CredentialsManager()
        self._connections = {}  # Store DuckDB connections
        self._attached_sources = {}  # Store attached source information
        self.logger = logger

    def attach_source(self, source: str, database: str, dest: str) -> bool:
        """
        Attach a database source to DuckDB.
        Currently supports PostgreSQL and MySQL sources.

        Args:
            source (str): Source identifier (e.g., 'postgresql/postgres_source' or 'mysql/mysql_source')
            database (str): Database name to connect to
            dest (str): Destination name in DuckDB

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get credentials for the source
            source_type = source.split('/')[0]
            if source_type in ['postgresql', 'mysql']:
                # Try to get credentials using UUID
                creds = self._credentials_manager.get_credentials_by_code('FAKEUUID', type=source_type)
                if not creds:
                    self.logger.error(f"No credentials found for source {source}")
                    return False

                if source_type == 'postgresql':
                    # Install and load PostgreSQL extension
                    self._get_duckdb_connection().install_extension("postgres")
                    self._get_duckdb_connection().load_extension("postgres")
                    extension_prefix = "postgres"
                    # Build PostgreSQL connection string
                    conn_str = (
                        f"host={creds['host']} "
                        f"port={creds['port']} "
                        f"user={creds['user']} "
                        f"password={creds['password']} "
                        f"database={database}"
                    )
                else:  # mysql
                    # Install and load MySQL extension
                    self._get_duckdb_connection().install_extension("mysql")
                    self._get_duckdb_connection().load_extension("mysql")
                    extension_prefix = "mysql"
                    # Build MySQL connection string
                    conn_str = (
                        f"host={creds['host']} "
                        f"port={creds['port']} "
                        f"user={creds['user']} "
                        f"passwd={creds['password']} "
                        f"db={database}"
                    )

                # Attach database
                self._get_duckdb_connection().sql(f"ATTACH '{extension_prefix}:{conn_str}' AS {dest}")
                self._attached_sources[dest] = {
                    'type': source_type,
                    'database': database
                }
                return True
            else:
                self.logger.error(f"Unsupported source type: {source_type}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to attach {source_type} source: {str(e)}")
            return False

    def get_duckdb_connection(self) -> Optional[duckdb.DuckDBPyConnection]:
        """
        Get or create a DuckDB connection.

        Returns:
            DuckDB connection object or None if creation fails
        """
        return self._get_duckdb_connection()

    def _get_duckdb_connection(self) -> Optional[duckdb.DuckDBPyConnection]:
        """
        Internal method to get or create a DuckDB connection.

        Returns:
            DuckDB connection object or None if creation fails
        """
        try:
            if 'default' not in self._connections:
                # Create new in-memory DuckDB connection
                conn = duckdb.connect(database=':memory:', read_only=False)
                self._connections['default'] = conn
                self.logger.info("Created new DuckDB connection")
            return self._connections['default']
        except Exception as e:
            self.logger.error(f"Failed to create DuckDB connection: {str(e)}")
            return None

    def get_attached_sources(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about attached sources.

        Returns:
            Dict containing information about attached sources
        """
        return self._attached_sources.copy() 