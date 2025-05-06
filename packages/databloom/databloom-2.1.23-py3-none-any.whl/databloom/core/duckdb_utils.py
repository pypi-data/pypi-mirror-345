"""
DuckDB utilities for reading various data formats.
"""
import duckdb
import logging
from typing import Optional, Union, List, Dict
import pandas as pd
import threading

logger = logging.getLogger(__name__)

class DuckDBReader:
    def __init__(self, config: Optional[dict] = None):
        """Initialize DuckDB reader with optional configuration.
        
        Args:
            config (dict, optional): Configuration for DuckDB connection
                s3_endpoint (str): S3 endpoint URL
                s3_access_key (str): S3 access key
                s3_secret_key (str): S3 secret key
                max_connections (int): Maximum number of concurrent connections (default: 5)
        """
        self.conn = duckdb.connect()
        self._connections: Dict[str, duckdb.DuckDBPyConnection] = {}
        self._connection_lock = threading.Lock()
        self.max_connections = config.get("max_connections", 5) if config else 5
        
        if config:
            self._setup_s3(config)

    def _setup_s3(self, config: dict):
        """Configure S3 settings for DuckDB."""
        s3_settings = {
            "s3_endpoint": config.get("s3_endpoint", "localhost:9000"),
            "s3_access_key_id": config.get("s3_access_key", "admin"),
            "s3_secret_access_key": config.get("s3_secret_key", "password"),
            "s3_url_style": "path",
            "s3_use_ssl": "false"
        }
        
        for key, value in s3_settings.items():
            self.conn.execute(f"SET s3_region='us-east-1';")
            self.conn.execute(f"SET {key}='{value}';")

    def _get_connection(self, db_type: str, dsn: str) -> duckdb.DuckDBPyConnection:
        """Get or create a database connection.
        
        Args:
            db_type: Type of database ('mysql' or 'postgres')
            dsn: Connection string
            
        Returns:
            DuckDB connection object
            
        Raises:
            ValueError: If connection limit is reached
        """
        conn_key = f"{db_type}:{dsn}"
        
        with self._connection_lock:
            # Check if connection exists and is valid
            if conn_key in self._connections:
                try:
                    # Test connection with simple query
                    self._connections[conn_key].execute("SELECT 1")
                    return self._connections[conn_key]
                except:
                    # Connection is invalid, remove it
                    self._cleanup_connection(conn_key)
            
            # Check connection limit
            if len(self._connections) >= self.max_connections:
                raise ValueError(f"Maximum number of connections ({self.max_connections}) reached")
            
            # Create new connection
            conn = duckdb.connect()
            conn.execute(f"INSTALL {db_type};")
            conn.execute(f"LOAD {db_type};")

            # Extract connection parameters from DSN
            if db_type == 'mysql':
                params = dict(p.split('=') for p in dsn.split(' ') if '=' in p)
                attach_cmd = (
                    f"ATTACH '{dsn}' AS {db_type}_db "
                    f"(TYPE mysql);"
                )
            else:  # PostgreSQL
                attach_cmd = f"ATTACH '{dsn}' AS {db_type}_db (TYPE {db_type});"

            conn.execute(attach_cmd)
            
            self._connections[conn_key] = conn
            return conn

    def _cleanup_connection(self, conn_key: str):
        """Clean up a database connection.
        
        Args:
            conn_key: Connection key to cleanup
        """
        if conn_key in self._connections:
            try:
                db_type = conn_key.split(":")[0]
                self._connections[conn_key].execute(f"DETACH {db_type}_db;")
                self._connections[conn_key].close()
            except Exception as e:
                logger.warning(f"Error cleaning up connection {conn_key}: {e}")
            finally:
                del self._connections[conn_key]

    def cleanup_all_connections(self):
        """Clean up all database connections."""
        with self._connection_lock:
            for conn_key in list(self._connections.keys()):
                self._cleanup_connection(conn_key)

    def read_parquet(self, path: Union[str, List[str]], columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Read Parquet file(s) into a DataFrame.
        
        Args:
            path: Path or list of paths to Parquet files (local or S3)
            columns: List of columns to read (optional)
        
        Returns:
            pandas.DataFrame: Data from Parquet file(s)
        """
        try:
            if isinstance(path, list):
                paths = ",".join([f"'{p}'" for p in path])
                query = f"SELECT * FROM read_parquet([{paths}])"
            else:
                query = f"SELECT * FROM read_parquet('{path}')"

            if columns:
                cols = ",".join(columns)
                query = query.replace("*", cols)

            return self.conn.execute(query).df()
        except Exception as e:
            logger.error(f"Error reading Parquet file: {e}")
            raise

    def read_json(self, path: Union[str, List[str]], auto_detect: bool = True) -> pd.DataFrame:
        """Read JSON file(s) into a DataFrame.
        
        Args:
            path: Path or list of paths to JSON files (local or S3)
            auto_detect: Automatically detect schema (default: True)
        
        Returns:
            pandas.DataFrame: Data from JSON file(s)
        """
        try:
            if isinstance(path, list):
                paths = ",".join([f"'{p}'" for p in path])
                query = f"SELECT * FROM read_json_auto([{paths}])" if auto_detect else f"SELECT * FROM read_json([{paths}])"
            else:
                query = f"SELECT * FROM read_json_auto('{path}')" if auto_detect else f"SELECT * FROM read_json('{path}')"

            return self.conn.execute(query).df()
        except Exception as e:
            logger.error(f"Error reading JSON file: {e}")
            raise

    def read_csv(self, path: Union[str, List[str]], **kwargs) -> pd.DataFrame:
        """Read CSV file(s) into a DataFrame with options.
        
        Args:
            path: Path or list of paths to CSV files (local or S3)
            **kwargs: Additional CSV reading options
                delimiter: Field delimiter (default: ',')
                header: Whether file has header (default: True)
                columns: List of column names
                skip: Number of rows to skip
        
        Returns:
            pandas.DataFrame: Data from CSV file(s)
        """
        try:
            options = []
            if kwargs.get("delimiter"):
                options.append(f"delim='{kwargs['delimiter']}'")
            if kwargs.get("header") is False:
                options.append("header=False")
            if kwargs.get("skip"):
                options.append(f"skip={kwargs['skip']}")

            options_str = ", ".join(options)
            
            if isinstance(path, list):
                paths = ",".join([f"'{p}'" for p in path])
                query = f"SELECT * FROM read_csv_auto([{paths}]{', ' + options_str if options_str else ''})"
            else:
                query = f"SELECT * FROM read_csv_auto('{path}'{', ' + options_str if options_str else ''})"

            # If columns are specified, rename them after reading
            result = self.conn.execute(query).df()
            if kwargs.get("columns"):
                result.columns = kwargs["columns"]
            return result
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise

    def read_mysql(self, dsn: str, query: str) -> pd.DataFrame:
        """Read data from MySQL using a query.
        
        Args:
            dsn: MySQL connection string
            query: SQL query to execute
            
        Returns:
            pandas.DataFrame: Query results
            
        Raises:
            Exception: If connection fails or query errors
        """
        try:
            # Validate DSN format
            if not all(x in dsn for x in ['host=', 'user=', 'password=', 'database=']):
                raise ValueError("DSN must include host, user, password and database")
            
            # Get connection and execute query
            conn = self._get_connection('mysql', dsn)
            result = conn.execute(query).df()
            return result
            
        except Exception as e:
            logger.error(f"Error reading from MySQL: {e}")
            raise

    def read_postgresql(self, dsn: str, query: str) -> pd.DataFrame:
        """Read data from PostgreSQL using a query.
        
        Args:
            dsn: PostgreSQL connection string
            query: SQL query to execute
            
        Returns:
            pandas.DataFrame: Query results
            
        Raises:
            Exception: If connection fails or query errors
        """
        try:
            # Validate DSN format
            if not all(x in dsn for x in ['host=', 'user=', 'password=', 'database=']):
                raise ValueError("DSN must include host, user, password and database")
            
            # Get connection and execute query
            conn = self._get_connection('postgres', dsn)
            result = conn.execute(query).df()
            return result
            
        except Exception as e:
            logger.error(f"Error reading from PostgreSQL: {e}")
            raise

    def __del__(self):
        """Clean up connections when object is destroyed."""
        self.cleanup_all_connections()
        if hasattr(self, 'conn'):
            self.conn.close() 