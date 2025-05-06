"""
DuckDB Utilities Module.

This module provides utilities for working with DuckDB connections and operations.
"""

import duckdb
import os
import pandas as pd
from typing import Dict, Optional, Any

class DatabaseConnector:
    """
    A class for managing DuckDB database connections and operations.
    """

    def __init__(self, database: str = ":memory:"):
        """
        Initialize DuckDB connection.
        
        Args:
            database: Path to the DuckDB database file
        """
        self._conn = duckdb.connect(database=database, read_only=False)
        
        # Install and load required extensions
        self._conn.execute("INSTALL httpfs;")
        self._conn.execute("INSTALL iceberg;")
        self._conn.execute("LOAD httpfs;")
        self._conn.execute("LOAD iceberg;")
        
        # Get S3 credentials from environment
        access_key = os.getenv("AWS_ACCESS_KEY_ID", "admin")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "password")
        endpoint = os.getenv("AWS_ENDPOINT", "http://localhost:9000")
        region = os.getenv("AWS_REGION", "us-east-1")
        
        # Configure S3 settings
        self._conn.execute(f"""
            SET s3_endpoint='{endpoint}';
            SET s3_access_key_id='{access_key}';
            SET s3_secret_access_key='{secret_key}';
            SET s3_region='{region}';
            SET s3_url_style='path';
            SET s3_use_ssl=false;
        """)
        
        # Create a secret for S3 access
        self._conn.execute(f"""
            CREATE OR REPLACE SECRET s3_cred (
                TYPE S3,
                KEY_ID '{access_key}',
                SECRET '{secret_key}',
                ENDPOINT '{endpoint}',
                REGION '{region}'
            );
        """)
        
        # Configure Iceberg settings
        self._conn.execute("""
            SET enable_object_cache=true;
            SET enable_http_metadata_cache=true;
        """)
        
        self._db_cache: Dict[str, Dict] = {}  # Cache for database connections

    def _build_connection_string(self, db_type: str, **kwargs) -> str:
        """
        Build a connection string for the specified database type.

        Args:
            db_type: The type of database (e.g., "postgres", "mysql")
            **kwargs: Connection parameters

        Returns:
            A connection string suitable for DuckDB's ATTACH command
        """
        if db_type == "postgres":
            # Get from environment if not provided
            host = kwargs.get("host") or os.environ.get("POSTGRES_HOST")
            port = kwargs.get("port") or os.environ.get("POSTGRES_PORT", "5432")
            database = kwargs.get("database") or os.environ.get("POSTGRES_DB")
            user = kwargs.get("user") or os.environ.get("POSTGRES_USER")
            password = kwargs.get("password") or os.environ.get("POSTGRES_PASSWORD")

            if not all([host, port, database, user, password]):
                raise ValueError(
                    "Missing required PostgreSQL connection parameters. "
                    "Provide them as arguments or set environment variables."
                )

            return f"host={host} port={port} database={database} user={user} password={password}"

        elif db_type == "mysql":
            # Similar implementation for MySQL
            host = kwargs.get("host") or os.environ.get("MYSQL_HOST")
            port = kwargs.get("port") or os.environ.get("MYSQL_PORT", "3306")
            database = kwargs.get("database") or os.environ.get("MYSQL_DATABASE")
            user = kwargs.get("user") or os.environ.get("MYSQL_USER")
            password = kwargs.get("password") or os.environ.get("MYSQL_PASSWORD")

            if not all([host, port, database, user, password]):
                raise ValueError(
                    "Missing required MySQL connection parameters. "
                    "Provide them as arguments or set environment variables."
                )

            return f"host={host} port={port} database={database} user={user} password={password}"

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def attach_local_file(self, file_type: str, path: str, table_name: str) -> None:
        """
        Attach a local file to DuckDB.
        
        Args:
            file_type: Type of file (csv, parquet, etc.)
            path: Path to the file
            table_name: Name for the table
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
            
        query = f"CREATE TABLE {table_name} AS SELECT * FROM read_{file_type}_auto('{path}')"
        self._conn.execute(query)
        
    def attach_web_file(self, file_type: str, url: str, table_name: str) -> None:
        """
        Attach a file from a web URL to DuckDB.
        
        Args:
            file_type: Type of file (csv, parquet, etc.)
            url: URL of the file
            table_name: Name for the table
        """
        query = f"CREATE TABLE {table_name} AS SELECT * FROM read_{file_type}_auto('{url}')"
        self._conn.execute(query)
        
    def attach_s3_file(self, file_type: str, path: str, table_name: str, 
                       source_id: str, credentials: Dict[str, str]) -> None:
        """
        Attach a file from S3 to DuckDB.
        
        Args:
            file_type: Type of file (csv, parquet, etc.)
            path: S3 path to the file
            table_name: Name for the table
            source_id: Unique identifier for the S3 source
            credentials: S3 credentials dictionary
        """
        # Create S3 secret if different from default
        if (credentials["access_key"] != "admin" or 
            credentials["secret_key"] != "password" or 
            credentials["endpoint"] != "localhost:9000"):
            
            self._conn.execute(f"""
                CREATE OR REPLACE SECRET {source_id} (
                    TYPE S3,
                    KEY_ID '{credentials["access_key"]}',
                    SECRET '{credentials["secret_key"]}',
                    ENDPOINT '{credentials["endpoint"]}',
                    REGION 'us-east-1'
                );
            """)
            secret_name = source_id
        else:
            secret_name = "s3_cred"
        
        # Create table from S3 file
        query = f"""
            CREATE TABLE {table_name} AS 
            SELECT * FROM read_{file_type}('s3://{path}', secret_key='{secret_name}')
        """
        self._conn.execute(query)
        
    def attach_database(self, db_name: str, db_type: str,
                       use_environment_variables: bool = True,
                       read_only: bool = True, **connection_params) -> None:
        """
        Attach an external database to DuckDB.
        
        Args:
            db_name: Name for the attached database
            db_type: Type of database (postgres, mysql)
            use_environment_variables: Whether to use environment variables
            read_only: Whether the connection should be read-only
            **connection_params: Additional connection parameters
        """
        if use_environment_variables:
            conn_string = self._build_connection_string(db_type)
        else:
            conn_string = self._build_connection_string(db_type, **connection_params)
            
        mode = "READ_ONLY" if read_only else ""
        query = f"ATTACH '{conn_string}' AS {db_name} (TYPE {db_type} {mode})"
        
        try:
            self._conn.execute(query)
            self._db_cache[db_name] = {
                "type": db_type,
                "conn_string": conn_string,
                "read_only": read_only
            }
        except Exception as e:
            raise Exception(f"Failed to attach {db_type} database: {str(e)}")
        
    def execute_sql(self, query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as a DataFrame.
        
        Args:
            query: SQL query to execute
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            return self._conn.execute(query).df()
        except Exception as e:
            if "iceberg_scan" in query:
                # Try to fix the path format
                if "s3a://" in query:
                    query = query.replace("s3a://", "s3://")
                if "secret_key" not in query:
                    query = query.replace("iceberg_scan('", "iceberg_scan('", 1)
                    query = query.replace("')", "', secret_key='s3_cred')", 1)
                return self._conn.execute(query).df()
            raise e
        
    def execute(self, query: str) -> None:
        """
        Execute a SQL query without returning results.
        
        Args:
            query: SQL query to execute
        """
        self._conn.execute(query)
        
    def close(self) -> None:
        """Close the DuckDB connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def detach_database(self, db_name: str):
        """
        Detach a database from DuckDB.

        Args:
            db_name: The name of the attached database to detach
        """
        if db_name not in self._db_cache:
            raise ValueError(f"Database {db_name} is not attached")

        try:
            self._conn.execute(f"DETACH {db_name}")
            del self._db_cache[db_name]
        except Exception as e:
            raise Exception(f"Failed to detach database {db_name}: {str(e)}")

    def copy_table_to_duckdb(
        self,
        source_db_name: str,
        source_table_name: str,
        dest_table_name: str,
        schema: Optional[str] = None
    ):
        """
        Copy a table from an attached database to DuckDB.

        Args:
            source_db_name: The name of the attached source database
            source_table_name: The name of the table in the source database
            dest_table_name: The name for the new table in DuckDB
            schema: Optional schema name for the source table
        """
        if source_db_name not in self._db_cache:
            raise ValueError(f"Source database {source_db_name} is not attached")

        try:
            source_path = (
                f"{source_db_name}.{schema}.{source_table_name}"
                if schema
                else f"{source_db_name}.{source_table_name}"
            )
            self._conn.execute(f"CREATE TABLE {dest_table_name} AS SELECT * FROM {source_path}")
        except Exception as e:
            raise Exception(f"Failed to copy table: {str(e)}")

    def copy_table_from_duckdb(
        self,
        source_table_name: str,
        dest_db_name: str,
        dest_table_name: str,
        schema: Optional[str] = None
    ):
        """
        Copy a table from DuckDB to an attached database.

        Args:
            source_table_name: The name of the source table in DuckDB
            dest_db_name: The name of the attached destination database
            dest_table_name: The name for the new table in the destination
            schema: Optional schema name for the destination table
        """
        if dest_db_name not in self._db_cache:
            raise ValueError(f"Destination database {dest_db_name} is not attached")

        if self._db_cache[dest_db_name]["read_only"]:
            raise ValueError(f"Cannot copy to read-only database {dest_db_name}")

        try:
            dest_path = (
                f"{dest_db_name}.{schema}.{dest_table_name}"
                if schema
                else f"{dest_db_name}.{dest_table_name}"
            )
            self._conn.execute(f"COPY (SELECT * FROM {source_table_name}) TO {dest_path}")
        except Exception as e:
            raise Exception(f"Failed to copy table: {str(e)}")

    def list_tables(self, db_name: str) -> pd.DataFrame:
        """
        List all tables in an attached database.

        Args:
            db_name: The name of the attached database

        Returns:
            DataFrame containing table information
        """
        if db_name not in self._db_cache:
            raise ValueError(f"Database {db_name} is not attached")

        try:
            return self._conn.execute(f"SHOW TABLES FROM {db_name}").df()
        except Exception as e:
            raise Exception(f"Failed to list tables: {str(e)}")

    def clear_cache(self, db_type: Optional[str] = None):
        """
        Clear the database connection cache.

        Args:
            db_type: Optional database type to clear only specific type connections
        """
        if db_type:
            # Clear only connections of the specified type
            to_remove = [
                name for name, info in self._db_cache.items()
                if info["type"] == db_type
            ]
            for name in to_remove:
                self.detach_database(name)
        else:
            # Clear all connections
            for name in list(self._db_cache.keys()):
                self.detach_database(name) 