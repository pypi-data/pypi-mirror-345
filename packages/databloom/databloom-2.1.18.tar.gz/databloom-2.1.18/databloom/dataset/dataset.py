"""
Dataset class for handling data operations.
"""
import os
import logging
import pandas as pd
from typing import Optional, Dict, Any, Callable
import duckdb
from ..api.credentials import CredentialsManager
from ..api.nessie_metadata import NessieMetadataClient
from ..core.connector.postgresql import PostgreSQLConnector
from ..core.connector.mysql import MySQLConnector
from ..core.spark.session import SparkSessionManager
from pyspark.sql import DataFrame
import re

logger = logging.getLogger(__name__)

class Dataset:
    """Main Dataset class for handling data operations."""
    
    def __init__(self):
        """Initialize Dataset with required components."""
        self._duckdb_con = None
        self._nessie_client = NessieMetadataClient()
        self.credentials = CredentialsManager()
        self.spark = SparkSessionManager()
        self._connectors = {}
        
    def get_duck_con(self) -> duckdb.DuckDBPyConnection:
        """Get DuckDB connection."""
        if not self._duckdb_con:
            self._duckdb_con = duckdb.connect(":memory:")
            self._setup_duckdb()
        return self._duckdb_con
        
    def _setup_duckdb(self):
        """Setup DuckDB with required extensions and settings."""
        con = self.get_duck_con()
        
        # Install and load extensions
        con.execute("INSTALL httpfs;")
        con.execute("LOAD httpfs;")
        con.execute("INSTALL iceberg;")
        con.execute("LOAD iceberg;")
        
        # Get S3 credentials from manager
        s3_creds = self.credentials.get_s3_credentials()
        
        # Configure S3 settings
        con.execute(f"SET s3_endpoint='{s3_creds['endpoint']}';")
        con.execute(f"SET s3_region='{s3_creds['region']}';")
        con.execute(f"SET s3_access_key_id='{s3_creds['access_key']}';")
        con.execute(f"SET s3_secret_access_key='{s3_creds['secret_key']}';")
        con.execute("SET s3_url_style='path';")
        con.execute("SET s3_use_ssl=false;")
        con.execute("SET enable_http_metadata_cache=false;")
        con.execute("SET enable_object_cache=false;")
        con.execute("SET s3_uploader_max_parts_per_file=10000;")
        con.execute("SET memory_limit='5GB';")
        con.execute("SET s3_url_compatibility_mode=true;")
        
    def get_nessie_credentials(self, cred_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get Nessie credentials using UUID.
        
        Args:
            cred_uuid: UUID for credentials
            
        Returns:
            Dict containing Nessie credentials or None if not found
        """
        return self.credentials.get_credentials_by_code(cred_uuid)
    
    def connect_nessie(self, cred_uuid: str) -> bool:
        """
        Connect to Nessie using credentials.
        
        Args:
            cred_uuid: UUID for credentials
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        creds = self.get_nessie_credentials(cred_uuid)
        if not creds:
            return False
            
        try:
            # Basic validation of required fields
            required_fields = ['uri', 'ref', 'warehouse', 'io_impl']
            if not all(field in creds for field in required_fields):
                return False
                
            # Configure DuckDB for Nessie
            self._setup_duckdb()
            self.duck_run_sql(f"SET s3_endpoint='{creds['uri']}'")
            self.duck_run_sql(f"SET s3_access_key_id='{creds.get('access_key', '')}'")
            self.duck_run_sql(f"SET s3_secret_access_key='{creds.get('secret_key', '')}'")
            return True
        except Exception:
            return False
    
    def attach_source(self, source: str, database: str, dest: str) -> bool:
        """
        Attach a data source.
        
        Args:
            source: Source identifier (e.g. mysql/mysql_source)
            database: Database name
            dest: Destination name in context
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            creds = self.credentials.get_credentials_by_code(source)
            if not creds:
                return False
                
            if source.startswith('mysql'):
                connector = MySQLConnector(creds)
            elif source.startswith('postgresql'):
                connector = PostgreSQLConnector(creds)
            else:
                return False
                
            if connector.connect():
                self._connectors[dest] = connector
                return True
            return False
        except Exception:
            return False 

    def duck_run_sql(self, query: str) -> duckdb.DuckDBPyRelation:
        """Run a SQL query with DuckDB.
        
        Args:
            query: SQL query string. Use {{database.tablename}} for table references
            
        Returns:
            duckdb.DuckDBPyRelation: Query results
        """
        try:
            # For direct iceberg_scan queries, execute as is
            if 'iceberg_scan' in query:
                return self.get_duck_con().sql(query)
                
            # For template queries, resolve metadata
            import re
            table_refs = re.findall(r'\{\{([\w\.]+)\}\}', query)
            
            # Replace table references with table locations
            processed_query = query
            for table_ref in table_refs:
                # Get metadata from Nessie API
                table_name = table_ref.split('.')[-1]
                metadata = self._nessie_client.find_table_metadata(table_name)
                
                if not metadata:
                    raise ValueError(f"Could not find table {table_ref}")
                
                # Replace the table reference with the iceberg table scan
                processed_query = processed_query.replace(
                    f'{{{{{table_ref}}}}}',
                    f"iceberg_scan('s3a://nessie/default/{table_name}_3f2190e1-c083-48ea-b51e-4db498ef562c/metadata/00001-3fbe1cf6-74b6-4f22-bd2d-e4927c4e912b.metadata.json')"
                )
            
            logger.debug(f"Executing query: {processed_query}")
            return self.get_duck_con().sql(processed_query)
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    def read_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Read data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            **kwargs: Additional arguments passed to pandas.read_csv
            
        Returns:
            pd.DataFrame: DataFrame containing the CSV data
        """
        try:
            return pd.read_csv(file_path, **kwargs)
        except Exception as e:
            logger.error(f"Error reading CSV file {file_path}: {e}")
            raise

    def read_source(self, file_path: str, source_uuid: str = None, filters: Dict[str, Any] = None, transform_fn: Callable = None) -> pd.DataFrame:
        """
        Read data from a source with optional filtering and transformation.
        
        Args:
            file_path: Path to the source file
            source_uuid: Optional UUID for source credentials
            filters: Optional dictionary of filters to apply
            transform_fn: Optional function to transform the data
            
        Returns:
            pd.DataFrame: DataFrame containing the source data
        """
        try:
            # Get source credentials if UUID provided
            if source_uuid:
                creds = self.get_nessie_credentials(source_uuid)
                if not creds:
                    raise ValueError(f"No credentials found for UUID {source_uuid}")
            
            # Read the data
            df = self.read_csv(file_path)
            
            # Apply filters if provided
            if filters:
                for col, value in filters.items():
                    df = df[df[col] == value]
            
            # Apply transformation if provided
            if transform_fn:
                df = transform_fn(df)
            
            return df
        except Exception as e:
            logger.error(f"Error reading from source {file_path}: {e}")
            raise

    def read_spark_table(self, table_name: str) -> DataFrame:
        """
        Read a table from the data warehouse using Spark.
        
        Args:
            table_name: Name of the table to read
            
        Returns:
            DataFrame: Spark DataFrame containing the table data
        """
        try:
            # Get Spark session
            logger.info(f"Getting Spark session to read table {table_name}")
            spark = self.spark.get_session()
            if not spark:
                raise RuntimeError("Failed to create Spark session")
            
            # Read the table using Spark SQL
            table_path = f"nessie.default.{table_name}"
            logger.info(f"Reading table from path: {table_path}")
            
            try:
                df = spark.read.table(table_path)
                logger.info(f"Successfully read table {table_name}")
                return df
            except Exception as e:
                logger.error(f"Failed to read table {table_name}: {str(e)}")
                raise ValueError(f"Table {table_name} not found or inaccessible") from e
                
        except Exception as e:
            logger.error(f"Error reading Spark table {table_name}: {str(e)}")
            raise

    def write_spark_table(self, df: DataFrame, table_name: str) -> None:
        """
        Write a Spark DataFrame to the data warehouse.
        
        Args:
            df: Spark DataFrame to write
            table_name: Name of the target table
            
        Returns:
            None
        """
        try:
            # Get Spark session
            logger.info(f"Getting Spark session to write table {table_name}")
            spark = self.spark.get_session()
            if not spark:
                raise RuntimeError("Failed to create Spark session")
            
            # Write the DataFrame to the warehouse
            table_path = f"nessie.default.{table_name}"
            logger.info(f"Writing table to path: {table_path}")
            
            try:
                (df.write
                 .format("iceberg")
                 .mode("overwrite")
                 .saveAsTable(table_path))
                logger.info(f"Successfully wrote table {table_name}")
            except Exception as e:
                logger.error(f"Failed to write table {table_name}: {str(e)}")
                raise ValueError(f"Failed to write table {table_name}") from e
                
        except Exception as e:
            logger.error(f"Error writing Spark table {table_name}: {str(e)}")
            raise