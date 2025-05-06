"""
MySQL connector for DataBloom SDK.
"""
from typing import Dict, Any, Optional
import pymysql
from sqlalchemy import create_engine
import logging

logger = logging.getLogger(__name__)

class MySQLConnector:
    """MySQL connector class for handling MySQL-specific operations."""
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize MySQL connector.
        
        Args:
            credentials: Dictionary containing MySQL credentials
        """
        self.credentials = credentials
        self._connection = None
        self._engine = None
        
    def get_connection(self) -> pymysql.Connection:
        """Get MySQL connection."""
        if not self._connection:
            try:
                self._connection = pymysql.connect(
                    host=self.credentials['host'],
                    port=int(self.credentials['port']),
                    user=self.credentials['user'],
                    password=self.credentials['password'],
                    db=self.credentials.get('database', None),
                    charset='utf8mb4'
                )
            except Exception as e:
                logger.error(f"Error connecting to MySQL: {e}")
                raise
        return self._connection
        
    def get_engine(self, database: Optional[str] = None) -> Any:
        """
        Get SQLAlchemy engine for MySQL.
        
        Args:
            database: Optional database name to connect to
            
        Returns:
            SQLAlchemy engine instance
        """
        if not self._engine:
            db_name = database or self.credentials.get('database', '')
            try:
                self._engine = create_engine(
                    f"mysql+pymysql://{self.credentials['user']}:{self.credentials['password']}"
                    f"@{self.credentials['host']}:{self.credentials['port']}/{db_name}"
                )
            except Exception as e:
                logger.error(f"Error creating MySQL engine: {e}")
                raise
        return self._engine
        
    def get_version(self) -> str:
        """Get MySQL server version."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                return version
        except Exception as e:
            logger.error(f"Error getting MySQL version: {e}")
            raise
            
    def close(self):
        """Close all connections."""
        if self._connection:
            try:
                self._connection.close()
            except Exception as e:
                logger.error(f"Error closing MySQL connection: {e}")
            finally:
                self._connection = None
                
        if self._engine:
            try:
                self._engine.dispose()
            except Exception as e:
                logger.error(f"Error disposing MySQL engine: {e}")
            finally:
                self._engine = None
