"""
Core Dataset Module for reading Iceberg tables using DuckDB and PostgreSQL.
"""

import duckdb
import logging
import pandas as pd
from sqlalchemy import create_engine, text
import sqlalchemy.exc

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Dataset:
    """A class for reading Iceberg tables using DuckDB and PostgreSQL."""
    
    def __init__(self, name, db_type="duckdb", pg_config=None):
        """
        Initialize Dataset with either DuckDB or PostgreSQL connection.
        
        Args:
            name: Name of the dataset
            db_type: Type of database ("duckdb" or "postgres")
            pg_config: PostgreSQL configuration dictionary if using postgres
        """
        self.name = name
        self.db_type = db_type
        
        if db_type == "duckdb":
            self._conn = self._setup_duckdb()
        elif db_type == "postgres":
            if not pg_config:
                raise ValueError("PostgreSQL configuration required for postgres db_type")
            self._conn = self._setup_postgres(pg_config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _setup_duckdb(self):
        """Setup DuckDB with Iceberg and S3 configuration"""
        conn = duckdb.connect(database=":memory:", read_only=False)
        
        try:
            # Install and load required extensions
            conn.execute("INSTALL httpfs;")
            conn.execute("INSTALL iceberg;")
            conn.execute("LOAD httpfs;")
            conn.execute("LOAD iceberg;")
            
            # Configure S3 settings explicitly without http:// in endpoint
            conn.execute("""
                SET s3_endpoint='localhost:9000';
                SET s3_access_key_id='admin';
                SET s3_secret_access_key='password';
                SET s3_region='us-east-1';
                SET s3_url_style='path';
                SET s3_use_ssl=false;
            """)
            
            # Create a secret for S3 access
            conn.execute("""
                CREATE SECRET s3_cred (
                    TYPE S3,
                    KEY_ID 'admin',
                    SECRET 'password',
                    ENDPOINT 'localhost:9000',
                    REGION 'us-east-1'
                );
            """)
            
            return conn
        except Exception as e:
            raise Exception(f"Failed to setup DuckDB: {str(e)}")
            
    def _setup_postgres(self, pg_config):
        """Setup PostgreSQL connection"""
        try:
            conn_str = f"postgresql://{pg_config['user']}:{pg_config['password']}@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}"
            return create_engine(conn_str)
        except Exception as e:
            raise Exception(f"Failed to setup PostgreSQL: {str(e)}")
    
    def read_table(self, table_path: str) -> pd.DataFrame:
        """
        Read a table into a DataFrame.
        
        Args:
            table_path: Full path to the table (S3 path for Iceberg, table name for PostgreSQL)
            
        Returns:
            pd.DataFrame: Table contents
        """
        try:
            if self.db_type == "duckdb":
                query = f"""
                    SELECT * 
                    FROM iceberg_scan('{table_path}')
                """
                return self._conn.execute(query).df()
            else:
                return pd.read_sql(f"SELECT * FROM {table_path}", self._conn)
        except Exception as e:
            logger.error(f"Failed to read table: {str(e)}")
            raise
            
    def execute_sql(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame if it's a SELECT query"""
        try:
            if self.db_type == "duckdb":
                result = self._conn.execute(sql)
                try:
                    return result.df()
                except:
                    return pd.DataFrame()  # Return empty DataFrame for non-SELECT queries
            else:
                with self._conn.connect() as connection:
                    try:
                        # Try to execute as SELECT query
                        return pd.read_sql(sql, connection)
                    except sqlalchemy.exc.ResourceClosedError:
                        # If it's not a SELECT query, execute it and return empty DataFrame
                        connection.execute(text(sql))
                        connection.commit()
                        return pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to execute SQL: {str(e)}")
            raise
            
    def update_table(self, table_name: str, df: pd.DataFrame, if_exists="fail", schema=None):
        """Update table with DataFrame contents"""
        try:
            if schema:
                table_name = f"{schema}.{table_name}"
            if self.db_type == "duckdb":
                self._conn.register(f"df_{table_name}", df)
                self._conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df_{table_name}")
            else:
                # Create schema if it doesn't exist
                if schema:
                    with self._conn.connect() as connection:
                        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                        connection.commit()
                
                # Use pandas to_sql with the engine directly
                df.to_sql(
                    name=table_name.split('.')[-1] if '.' in table_name else table_name,
                    con=self._conn,
                    schema=schema,
                    if_exists=if_exists,
                    index=False
                )
        except Exception as e:
            logger.error(f"Failed to update table: {str(e)}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self._conn:
            if self.db_type == "duckdb":
                self._conn.close()
            self._conn = None 