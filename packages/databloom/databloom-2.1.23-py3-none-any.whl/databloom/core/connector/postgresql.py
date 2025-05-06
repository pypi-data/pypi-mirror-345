"""
PostgreSQL connector for DataBloom SDK.
"""
from typing import Dict, Any, Optional, List, Tuple
import psycopg2
from sqlalchemy import create_engine
import logging

logger = logging.getLogger(__name__)

class PostgreSQLConnector:
    """PostgreSQL connector class for handling PostgreSQL-specific operations."""
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize PostgreSQL connector.
        
        Args:
            credentials: Dictionary containing PostgreSQL credentials
        """
        self.credentials = credentials
        self._connection = None
        self._engine = None
        
    def get_connection(self) -> psycopg2.extensions.connection:
        """Get PostgreSQL connection."""
        if not self._connection:
            try:
                self._connection = psycopg2.connect(
                    host=self.credentials['host'],
                    port=int(self.credentials['port']),
                    user=self.credentials['user'],
                    password=self.credentials['password'],
                    database=self.credentials.get('database', None)
                )
            except Exception as e:
                logger.error(f"Error connecting to PostgreSQL: {e}")
                raise
        return self._connection
        
    def get_engine(self, database: Optional[str] = None) -> Any:
        """
        Get SQLAlchemy engine for PostgreSQL.
        
        Args:
            database: Optional database name to connect to
            
        Returns:
            SQLAlchemy engine instance
        """
        if not self._engine:
            db_name = database or self.credentials.get('database', '')
            try:
                self._engine = create_engine(
                    f"postgresql://{self.credentials['user']}:{self.credentials['password']}"
                    f"@{self.credentials['host']}:{self.credentials['port']}/{db_name}"
                )
            except Exception as e:
                logger.error(f"Error creating PostgreSQL engine: {e}")
                raise
        return self._engine
        
    def get_version(self) -> str:
        """Get PostgreSQL server version."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                return version
        except Exception as e:
            logger.error(f"Error getting PostgreSQL version: {e}")
            raise
            
    def list_tables(self, schema: str = "public") -> List[Tuple[str, str]]:
        """
        List all tables in the specified schema.
        
        Args:
            schema: Schema name to list tables from (default: public)
            
        Returns:
            List of tuples containing (table_name, table_type)
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name, table_type
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    ORDER BY table_name
                """, (schema,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error listing tables in schema {schema}: {e}")
            raise
            
    def get_table_schema(self, table_name: str, schema: str = "public") -> List[Tuple[str, str]]:
        """
        Get the schema information for a table.
        
        Args:
            table_name: Name of the table
            schema: Schema name (default: public)
            
        Returns:
            List of tuples containing (column_name, data_type)
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = %s
                    AND table_name = %s
                    ORDER BY ordinal_position
                """, (schema, table_name))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting schema for table {table_name}: {e}")
            raise
            
    def close(self):
        """Close all connections."""
        if self._connection:
            try:
                self._connection.close()
            except Exception as e:
                logger.error(f"Error closing PostgreSQL connection: {e}")
            finally:
                self._connection = None
                
        if self._engine:
            try:
                self._engine.dispose()
            except Exception as e:
                logger.error(f"Error disposing PostgreSQL engine: {e}")
            finally:
                self._engine = None
