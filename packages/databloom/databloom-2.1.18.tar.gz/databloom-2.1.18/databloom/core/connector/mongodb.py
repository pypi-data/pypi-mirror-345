"""
MongoDB connector for DataBloom SDK.
"""
from typing import Dict, Any, Optional, List, Union
from pymongo import MongoClient
import pandas as pd
import logging
import urllib.parse

logger = logging.getLogger(__name__)

class MongoDBConnector:
    """MongoDB connector class for handling MongoDB-specific operations."""
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize MongoDB connector.
        
        Args:
            credentials: Dictionary containing MongoDB credentials
        """
        self.credentials = credentials
        self._client = None
        self._db = None
        
    def connect(self, database: Optional[str] = None) -> Any:
        """
        Connect to MongoDB and return database instance.
        
        Args:
            database: Optional database name to connect to
            
        Returns:
            MongoDB database instance
        """
        if self._client is None:
            try:
                connection_string = self._build_connection_string()
                self._client = MongoClient(connection_string)
                # Test the connection
                self._client.admin.command('ping')
            except Exception as e:
                logger.error(f"Error connecting to MongoDB: {e}")
                raise
                
        db_name = database or self.credentials.get('database_name', 'mongodb')
        if not db_name:
            raise ValueError("Database name must be specified either in credentials or as parameter")
            
        self._db = self._client[db_name]
        return self._db
        
    def _build_connection_string(self) -> str:
        """Build MongoDB connection string from credentials."""
        host = self.credentials.get('host', 'localhost')
        port = self.credentials.get('port', 27017)
        username = urllib.parse.quote_plus(self.credentials.get('username', ''))
        password = urllib.parse.quote_plus(self.credentials.get('password', ''))
        database = self.credentials.get('database_name', 'mongodb')
        
        if username and password:
            return f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin"
        else:
            return f"mongodb://{host}:{port}/{database}"
            
    def read(self, collection: str, query: Optional[Dict] = None, 
             projection: Optional[Dict] = None, as_dataframe: bool = True) -> Union[List[Dict], pd.DataFrame]:
        """
        Read data from a MongoDB collection.
        
        Args:
            collection: Name of the collection to read from
            query: Optional MongoDB query filter
            projection: Optional fields to include/exclude
            as_dataframe: Whether to return results as pandas DataFrame (default: True)
            
        Returns:
            List of documents or pandas DataFrame
        """
        if self._db is None:
            raise ValueError("Not connected to MongoDB. Call connect() first.")
            
        try:
            # If no query is provided, get all documents
            if query is None:
                query = {}
                
            # Execute query with optional projection
            cursor = self._db[collection].find(query, projection)
            documents = list(cursor)
            
            if as_dataframe:
                # Convert to DataFrame
                df = pd.DataFrame(documents)
                # Remove MongoDB _id field if it exists
                if '_id' in df.columns:
                    df = df.drop('_id', axis=1)
                logger.info(f"Successfully read {len(df)} records from collection {collection}")
                return df
            else:
                logger.info(f"Successfully read {len(documents)} records from collection {collection}")
                return documents
                
        except Exception as e:
            logger.error(f"Error reading from MongoDB: {e}")
            return pd.DataFrame() if as_dataframe else []
            
    def write(self, collection: str, data: Union[pd.DataFrame, List[Dict]]) -> bool:
        """
        Write data to a MongoDB collection.
        
        Args:
            collection: Name of the collection to write to
            data: pandas DataFrame or list of dictionaries to write
            
        Returns:
            bool: True if write was successful
        """
        if self._db is None:
            raise ValueError("Not connected to MongoDB. Call connect() first.")
            
        try:
            # Convert DataFrame to list of dictionaries if needed
            if isinstance(data, pd.DataFrame):
                records = data.to_dict('records')
            else:
                records = data
                
            # Insert records
            result = self._db[collection].insert_many(records)
            logger.info(f"Successfully inserted {len(result.inserted_ids)} records to collection {collection}")
            return True
        except Exception as e:
            logger.error(f"Error writing to MongoDB: {e}")
            return False
            
    def get_version(self) -> str:
        """Get MongoDB server version."""
        if self._client is None:
            raise ValueError("Not connected to MongoDB. Call connect() first.")
            
        try:
            return self._client.server_info()['version']
        except Exception as e:
            logger.error(f"Error getting MongoDB version: {e}")
            raise
            
    def close(self):
        """Close MongoDB connection."""
        if self._client is not None:
            try:
                self._client.close()
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {e}")
            finally:
                self._client = None
                self._db = None 