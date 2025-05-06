"""
Spark PostgreSQL connector for DataBloom SDK.
"""
from typing import Dict, Any, Optional
import logging
from pyspark.sql import DataFrame, SparkSession
import traceback

logger = logging.getLogger(__name__)

class SparkPostgreSQLConnector:
    """Spark PostgreSQL connector class for handling Spark-specific PostgreSQL operations."""
    
    def __init__(self, spark: SparkSession, credentials: dict):
        """Initialize the Spark PostgreSQL connector.
        
        Args:
            spark: SparkSession instance
            credentials: Dictionary containing PostgreSQL credentials
        """
        self.spark = spark
        self.credentials = credentials
        logger.info("Initialized Spark PostgreSQL connector")
        
    def read_table(self, database: str, table: str, schema: str = "public") -> DataFrame:
        """
        Read a table from PostgreSQL using Spark JDBC.
        
        Args:
            database: Database name to read from
            table: Table name to read
            schema: Schema name (default: public)
            
        Returns:
            DataFrame: Spark DataFrame containing table data
        """
        try:
            # Build the JDBC URL with schema information
            jdbc_url = f"jdbc:postgresql://{self.credentials['host']}:{self.credentials['port']}/{database}"
            logger.info(f"Reading table {schema}.{table} from {jdbc_url}")
            
            # Build the full table name with schema
            full_table = f"{schema}.{table}"
            
            # Configure JDBC options
            jdbc_options = {
                "url": jdbc_url,
                "dbtable": full_table,
                "user": self.credentials["user"],
                "password": self.credentials["password"],
                "driver": "org.postgresql.Driver",
                "currentSchema": schema
            }
            
            # Log options for debugging (excluding sensitive info)
            safe_options = {k: v for k, v in jdbc_options.items() if k not in ["password"]}
            logger.info(f"JDBC options: {safe_options}")
            
            # Execute the read operation
            df = self.spark.read.format("jdbc").options(**jdbc_options).load()
            
            # Log success
            logger.info(f"Successfully read {df.count()} rows from {full_table}")
            return df
            
        except Exception as e:
            logger.error(f"Error reading table {schema}.{table} from PostgreSQL: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise
            
    def write_table(self, df: DataFrame, database: str, table: str, schema: str = "public", mode: str = "overwrite"):
        """
        Write a DataFrame to PostgreSQL using Spark JDBC.
        
        Args:
            df: Spark DataFrame to write
            database: Database name to write to
            table: Table name to write
            schema: Schema name (default: public)
            mode: Write mode (default: overwrite)
        """
        try:
            # Build the JDBC URL with schema information
            jdbc_url = f"jdbc:postgresql://{self.credentials['host']}:{self.credentials['port']}/{database}"
            logger.info(f"Writing to table {schema}.{table} at {jdbc_url}")
            
            # Build the full table name with schema
            full_table = f"{schema}.{table}"
            
            # Configure JDBC options
            jdbc_options = {
                "url": jdbc_url,
                "dbtable": full_table,
                "user": self.credentials["user"],
                "password": self.credentials["password"],
                "driver": "org.postgresql.Driver",
                "currentSchema": schema
            }
            
            # Log options for debugging (excluding sensitive info)
            safe_options = {k: v for k, v in jdbc_options.items() if k not in ["password"]}
            logger.info(f"JDBC options: {safe_options}")
            
            # Execute the write operation
            df.write.format("jdbc").options(**jdbc_options).mode(mode).save()
            
            # Log success
            logger.info(f"Successfully wrote {df.count()} rows to {full_table}")
            
        except Exception as e:
            logger.error(f"Error writing to table {schema}.{table} in PostgreSQL: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise
            
    def execute_query(self, database: str, query: str) -> DataFrame:
        """
        Execute a SQL query on PostgreSQL using Spark JDBC.
        
        Args:
            database: Database name to query
            query: SQL query to execute
            
        Returns:
            DataFrame: Spark DataFrame containing query results
        """
        try:
            # Build the JDBC URL
            jdbc_url = f"jdbc:postgresql://{self.credentials['host']}:{self.credentials['port']}/{database}"
            logger.info(f"Executing query on {jdbc_url}")
            
            # Configure JDBC options
            jdbc_options = {
                "url": jdbc_url,
                "query": query,
                "user": self.credentials["user"],
                "password": self.credentials["password"],
                "driver": "org.postgresql.Driver"
            }
            
            # Log options for debugging (excluding sensitive info)
            safe_options = {k: v for k, v in jdbc_options.items() if k not in ["password"]}
            logger.info(f"JDBC options: {safe_options}")
            
            # Execute the query
            df = self.spark.read.format("jdbc").options(**jdbc_options).load()
            
            # Log success
            logger.info(f"Successfully executed query, returned {df.count()} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error executing query on PostgreSQL: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise 