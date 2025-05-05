"""
Main context class for DataBloom SDK.
"""
import logging
import os
from typing import Optional, Dict, Any, List, Callable, Union
import duckdb
from sqlalchemy import create_engine
from pyspark.sql import SparkSession
import pyspark
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime
from sqlalchemy import text
from pyspark.sql.functions import lit
import urllib.parse
from ..dataset.dataset import Dataset
from ..api.credentials import CredentialsManager
from ..core.connector.mysql import MySQLConnector
from ..core.connector.postgresql import PostgreSQLConnector
from ..core.connector.mongodb import MongoDBConnector
from ..core.connector.spark_postgresql import SparkPostgreSQLConnector
from ..core.connector.ggsheet import read_ggsheet
from ..core.spark.session import SparkSessionManager
from .lighter_context import LighterContext

logger = logging.getLogger(__name__)

class DataBloomContext:
    """Main context class for DataBloom SDK."""
    
    def __init__(self, base_url: str = "https://dev-sdk.ird.vng.vn/v1/sources/", lighter_api_url: str = "https://dev-sdk.ird.vng.vn/v1/sources/"):
        """Initialize DataBloom context."""
        self._dataset = Dataset()
        self._credentials = CredentialsManager()
        self._duckdb_con = None
        self._attached_sources = {}
        self._connectors = {}
        self._spark_manager = SparkSessionManager()
        self._spark_connectors = {}
        self._lighter_context = None
        self._mongodb_connectors = {}
        self._base_url = base_url
        self._lighter_api_url = lighter_api_url
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
        
        # # Get S3 credentials from manager
        # s3_creds = self._credentials.get_s3_credentials()
        
        # # Configure S3 settings
        # con.execute(f"SET s3_endpoint='{s3_creds['endpoint']}';")
        # con.execute(f"SET s3_region='{s3_creds['region']}';")
        # con.execute(f"SET s3_access_key_id='{s3_creds['access_key']}';")
        # con.execute(f"SET s3_secret_access_key='{s3_creds['secret_key']}';")
        con.execute("SET s3_url_style='path';")
        con.execute("SET s3_use_ssl=false;")
        con.execute("SET enable_http_metadata_cache=false;")
        con.execute("SET enable_object_cache=false;")
        con.execute("SET s3_uploader_max_parts_per_file=10000;")
        con.execute("SET memory_limit='5GB';")
        con.execute("SET s3_url_compatibility_mode=true;")
        
    def attach_source(self, source: str, database: str, dest: str) -> bool:
        """
        Attach a data source to DuckDB.
        
        Args:
            source: Source identifier in format 'type/name'
            database: Database name to connect to
            dest: Destination name for the attached source
            
        Returns:
            bool: True if source was attached successfully
        """
        source_type, source_name = source.split("/")
        creds = self._credentials.get_credentials_by_code(source)
        
        if not creds:
            raise ValueError(f"No credentials found for {source}")
            
        try:
            if source_type == "mysql":
                # Install MySQL extension if needed
                self.get_duck_con().execute("INSTALL mysql;")
                self.get_duck_con().execute("LOAD mysql;")
                
                # Create MySQL connector
                connector = MySQLConnector(creds)
                self._connectors[dest] = connector
                
                # Build connection string
                conn_str = (
                    f"host={creds['host']}"
                    f" port={creds['port']}"
                    f" user={creds['user']}"
                    f" password={creds['password']}"
                    f" database={database}"
                )
                
                # Attach MySQL database
                self.get_duck_con().execute(f"ATTACH '{conn_str}' AS {dest} (TYPE mysql);")
                self._attached_sources[dest] = {"type": "mysql", "database": database}
                return True
                
            elif source_type == "postgresql":
                # Install and load PostgreSQL extension
                try:
                    self.get_duck_con().execute("INSTALL postgres;")
                    self.get_duck_con().execute("LOAD postgres;")
                except Exception as e:
                    logger.error(f"Failed to install/load PostgreSQL extension: {e}")
                    raise

                # Build connection string
                conn_str = (
                    f"host={creds['host']} "
                    f"port={creds['port']} "
                    f"user={creds['username']} "
                    f"password={creds['password']} "
                    f"dbname={database}"
                )
                
                # Attach PostgreSQL database
                self.get_duck_con().execute(f"ATTACH '{conn_str}' AS {dest} (TYPE postgres);")
                self._attached_sources[dest] = {"type": "postgresql", "database": database}
                return True
                
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
                
        except Exception as e:
            logger.error(f"Error attaching source {source}: {e}")
            raise
            
    def create_sqlalchemy_engine(self, source: Optional[str] = None, database: Optional[str] = None):
        """
        Create a SQLAlchemy engine for database connection.
        
        Args:
            source: Optional source identifier in format 'type/alias'
            database: Optional database name
            
        Returns:
            SQLAlchemy engine instance
        """
        
        if source is None:
            engine = self._credentials.get_credentials_by_code()
            connection_string = f"trino://{engine['username']}:{urllib.parse.quote_plus(engine['password'])}@{engine['host']}:{engine['port']}/{engine['catalog']}"
            return create_engine(connection_string)

        source_type, alias = source.split("/")
        if source_type not in ["postgresql", "mysql", "oracle", "mssql"]:
            raise Exception(f"Unsupported source type: {source_type}")
        
        # Verify database name
        if not isinstance(database, str):
            raise Exception("Database name must be a string")
        
        creds = self._credentials.get_credentials_by_code(source)
        
        if source_type == "postgresql":
            connection_string = f"postgresql://{creds['username']}:{urllib.parse.quote_plus(creds['password'])}@{creds['host']}:{creds['port']}/{database}"
        elif source_type == "mysql":  # mysql
            connection_string = f"mysql+pymysql://{creds['username']}:{urllib.parse.quote_plus(creds['password'])}@{creds['host']}:{creds['port']}/{database}"
        elif source_type == "mssql":
            connection_string = f"mssql+pymssql://{creds['username']}:{urllib.parse.quote_plus(creds['password'])}@{creds['host']}:{creds['port']}/{database}"
        elif source_type == "oracle":
            engine = create_engine( 
                f'oracle+oracledb://:@',  # Empty connection string as we'll use connect_args
                thick_mode=False,  # Use thin mode which doesn't need Oracle Client libraries
                connect_args={
                            "user": creds["username"],
                            "password": creds["password"],
                            "host": creds["host"],
                            "port": creds["port"],
                            "service_name": database
                }
            )
            return engine
        else:   
            raise Exception(f"Unsupported source type: {source_type}")
            
        engine = create_engine(connection_string)
        return engine
            
    def get_attached_sources(self) -> Dict[str, Dict[str, str]]:
        """Get dictionary of attached sources."""
        return self._attached_sources
        
    def get_connector(self, dest: str) -> Optional[Any]:
        """
        Get connector instance for an attached source.
        
        Args:
            dest: Destination name of the attached source
            
        Returns:
            Connector instance or None if not found
        """
        return self._connectors.get(dest)
        
    def duckdb_sql(self, query: str):
        """Execute a SQL query with DuckDB."""
        return self._dataset.duck_run_sql(query)
        
    def get_spark_session(self, app_name: str = "DataBloom", config: Dict[str, str] = {"cores": 1, "memory": "1g"}, mode: str = "local") -> SparkSession:
        """
        Get or create a Spark session.
        
        Args:
            app_name: Name for the Spark application
            config: Dictionary with configuration parameters:
                - cores: Number of cores to use
                - memory: Amount of memory to use (e.g. "1g")
            
        Returns:
            SparkSession instance
        """
        return self._spark_manager.get_session(app_name=app_name, config=config, mode=mode)

    def spark_write_data(self, df: pyspark.sql.DataFrame, source: Optional[str] = None, table: Optional[str] = None, mode: Optional[str] = "append"):
        """Write a Spark DataFrame to a table.
        
        Args:
            df: pyspark.sql.DataFrame to write
            source: Optional source identifier in format 'type/alias'
            table: Optional table name
            mode: Write mode ("overwrite" or "append")

        Returns:
            bool: True if write was successful
        """

        spark = self.get_spark_session()
        assert table is not None, "Table name is required"
        assert mode in ["overwrite", "append"], "Invalid mode"


        df_schema = self.read_data(query=f"select * from {table} limit 1")
        # check missing column then fill with NaN
        missing_columns = set(df_schema.columns) - set(df.columns)
        for col in missing_columns:
            logger.warning(f"Missing column: {col} when write to data default value is None")
            df = df.withColumn(col, lit(None))

        table_name = '.'.join(table.split(".")[-2:])
        if mode == "overwrite":
            spark.sql(f"TRUNCATE TABLE nessie.{table_name}")
        if source is None:
            table = f"nessie.{table_name}"
            try:
                (df.write
                .format("iceberg")
                .mode('append')
                .saveAsTable(table))
                logger.info(f"Successfully wrote table {table}")
            except Exception as e:
                logger.error(f"Failed to write table {table}: {str(e)}")
                raise ValueError(f"Failed to write table {table}") from e
            return True

        df.write.mode("append").saveAsTable(table)
        return True

    def spark_read_data(self, source: Optional[str] = None, database: Optional[str] = None, table: Optional[str] = None, query: Optional[str] = None):
        """Read data from a database table using Spark.
        
        Args:
            source: Optional source identifier in format 'type/alias'
            database: Optional database name
            table: Optional table name
            query: Optional SQL query

        Returns:
            pyspark.sql.DataFrame: DataFrame containing the query results
        """
        try:
            spark = self.get_spark_session()
            logger.info("Got Spark session")
            

            if source is None:
                if table:
                    table_name = '.'.join(table.split(".")[-2:])
                    table = f"nessie.{table_name}"
                    df = spark.table(table)
                elif query:
                    df = spark.sql(query)
                return df

            if source.startswith("postgresql/"):
                logger.info(f"Reading from PostgreSQL - source: {source}, database: {database}, table: {table}")
                try:
                    api_jdbc_url = self._credentials.get_jdbc_credentials(source=source, database=database)
                except Exception as e:
                    logger.error(f"Error getting JDBC credentials: {e}")
                    raise
            
                try:
                    if query:
                        df = spark.read \
                            .format("jdbc") \
                            .option("url", api_jdbc_url) \
                            .option("query", query) \
                            .option("driver", "org.postgresql.Driver") \
                            .option("fetchsize", "10000") \
                            .load()                        
                        logger.info("Successfully loaded DataFrame from PostgreSQL")
                        return df

                    if table:
                    # Read from PostgreSQL
                        df = spark.read \
                            .format("jdbc") \
                            .option("url", api_jdbc_url) \
                            .option("dbtable", table) \
                            .option("driver", "org.postgresql.Driver") \
                            .option("fetchsize", "10000") \
                            .load()
                        logger.info("Successfully loaded DataFrame from PostgreSQL")
                        return df
                except Exception as e:
                    logger.error(f"Error reading from PostgreSQL: {e}")
                    raise

            elif source.startswith("mysql/"):
                logger.info(f"Reading from MySQL - source: {source}, database: {database}, table: {table}")
                try:
                    api_jdbc_url = self._credentials.get_jdbc_credentials(source=source, database=database)
                except Exception as e:
                    logger.error(f"Error getting JDBC credentials: {e}")
                    raise

                try:
                    # Read from MySQL
                    if query:
                        df = spark.read \
                            .format("jdbc") \
                            .option("url", api_jdbc_url) \
                            .option("query", query) \
                            .option("driver", "com.mysql.cj.jdbc.Driver") \
                            .option("fetchsize", "10000") \
                            .load()
                    else:
                        # Handle table names
                        df = spark.read \
                            .format("jdbc") \
                            .option("url", api_jdbc_url) \
                            .option("dbtable", table) \
                            .option("driver", "com.mysql.cj.jdbc.Driver") \
                            .option("fetchsize", "10000") \
                            .load()
                    logger.info("Successfully loaded DataFrame from MySQL")
                    return df
                except Exception as e:
                    logger.error(f"Error reading from MySQL: {e}")
                    raise

            else:
                raise Exception(f"Unsupported source type: {source}")

        except Exception as e:
            logger.error(f"Error in spark_read_data: {e}")
            raise
        
    def close(self):
        """Close all connections and resources."""
        if self._duckdb_con:
            self._duckdb_con.close()
            self._duckdb_con = None
            
        if self._spark_manager:
            self._spark_manager.stop_session()

    def run_spark_job(self, code_fn: Callable, mode: str = "cluster", executors: Dict[str, Union[int, float]] = {"num_executors": 4, "cpu": 1, "mem": 1}, verbose: bool = False) -> Optional[dict]:
        """Run a Spark job with specified configuration
        
        Args:
            code_fn: Function containing the Spark code
            mode: Execution mode ("cluster" or "client")
            executors: Dictionary with executor configuration:
                - num_executors: Number of executors
                - cpu: CPU cores per executor
                - mem: Memory per executor in GB
        
        Returns:
            Dictionary containing job results if successful
        """
        if self._lighter_context is None:
            self._lighter_context = LighterContext(verbose=verbose, lighter_api_url=self._lighter_api_url)
        return self._lighter_context.run_spark_job(code_fn, mode, executors)

    def create_mongodb_connection(self, source: str, database: str = None) -> MongoDBConnector:
        """
        Create a MongoDB connection.
        
        Args:
            source: Source identifier in format 'type/name'
            database: Optional database name (default: None)
            
        Returns:
            MongoDB connector instance
        """
        try:
            # Get credentials for the source
            creds = self._credentials.get_credentials_by_code(source)
            if not creds:
                raise ValueError(f"No credentials found for {source}")
            
            # Initialize MongoDB connector
            mongo_connector = MongoDBConnector(creds)
            
            # Connect to database
            mongo_connector.connect(database)
            
            # Store connector
            self._mongodb_connectors[source] = mongo_connector
            
            return mongo_connector
        except Exception as e:
            logger.error(f"Error creating MongoDB connection: {e}")
            raise

    def read_mongodb_table(self, connector: MongoDBConnector, collection: str, 
                          query: Optional[Dict] = None, 
                          projection: Optional[Dict] = None) -> pd.DataFrame:
        """
        Read data from MongoDB collection into a pandas DataFrame.
        
        Args:
            connector: MongoDB connector instance
            collection: Name of the collection to read
            query: Optional MongoDB query filter
            projection: Optional fields to include/exclude
            
        Returns:
            pandas DataFrame containing the query results
        """
        try:
            return connector.read(collection, query, projection)
        except Exception as e:
            logger.error(f"Error reading from MongoDB: {e}")
            raise

    def write_mongodb_table(self, connector: MongoDBConnector, collection: str, 
                           data: Union[pd.DataFrame, List]) -> bool:
        """
        Write data to MongoDB collection.
        
        Args:
            connector: MongoDB connector instance
            collection: Name of the collection to write to
            data: pandas DataFrame or list of dictionaries to write
            
        Returns:
            bool: True if write was successful
        """
        try:
            return connector.write(collection, data)
        except Exception as e:
            logger.error(f"Error writing to MongoDB: {e}")
            raise

    def read_ggsheet(self, source: str, sheet: str, worksheetname: str) -> pd.DataFrame:
        """Read data from Google Sheet.
        
        Args:
            source: Source identifier in format 'google_sheet/name'
            sheet: Name of the Google Sheet
            worksheetname: Name of the worksheet within the sheet
            
        Returns:
            pd.DataFrame: Data from the Google Sheet
        """
        try:
            return read_ggsheet(source, sheet, worksheetname)
        except Exception as e:
            logger.error(f"Error reading Google Sheet: {e}")
            raise

    def run_sql_query(self, stmt: str, source: Optional[str] = None, database: Optional[str] = None) -> pd.DataFrame:
        """Run a SQL query on the specified database.
        
        Args:
            source: Source identifier in format 'type/name'
            database: Database name to query
            stmt: SQL query to execute
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            # Create SQLAlchemy engine
            engine = self.create_sqlalchemy_engine(source=source, database=database)
            
            # Execute query and return results as DataFrame
            result = pd.read_sql_query(stmt, engine)
            engine.dispose()

            return result
            
        except Exception as e:
            logger.error(f"Error running SQL query: {e}")
            raise 

    # Map pandas dtypes to SQLAlchemy types
    def get_sqlalchemy_type(self, dtype):
        if np.issubdtype(dtype, np.integer):
            return Integer
        elif np.issubdtype(dtype, np.floating):
            return Float
        elif np.issubdtype(dtype, np.datetime64):
            return DateTime
        else:
            # For string columns, calculate max length
            return String(length=200)

    def read_data(self, 
        table: Optional[str] = None, 
        source: Optional[str] = None, 
        database: Optional[str] = None,
        query: Optional[str] = None,
        columns: Optional[List[str]] = None
        ) -> pd.DataFrame:
        """Read data from a database table.
        
        Args:
            table: Table name to read from
            source: Source identifier in format 'type/name'
            database: Database name to read from
            query: SQL query to execute

        Returns:
            pd.DataFrame: Query results
        """
        try:
            # Create SQLAlchemy engine
            engine = self.create_sqlalchemy_engine(source=source, database=database)

            if query:
                # Execute query and return results as DataFrame
                result = pd.read_sql_query(sql=query, con=engine)
                engine.dispose()
                return result
            elif table:
                # Read from table
                schema, table = table.split(".")[-2:]
                try:
                    result = pd.read_sql_table(table_name=table, schema=schema, con=engine, columns=columns)
                except Exception as e:
                    result = pd.read_sql_query(f"select * from {table}", con=engine)
                engine.dispose()
                return result

        except Exception as e:
            logger.error(f"Error reading data from {database}.{table}: {str(e)}")
            raise


    def write_data(self, 
        df: pd.DataFrame,
        table: str, 
        mode: str = "append", 
        method: Optional[str] = "multi", 
        chunk_size: Optional[int] = 1000, 
        mapping_col: Optional[Dict[str, str]] = None, 
        dest: Optional[str] = None, 
        database: Optional[str] = None,
        index: bool = False
        ) -> bool:
        """Write data to a database table.
        
        Args:
            df: pandas DataFrame to write
            dest: Dest identifier in format 'type/name'
            database: Database name to write to
            table: Table name to write to
            mode: Write mode ("append" or "overwrite")
            method: Write method ("multi" or "single")
            chunk_size: Number of rows to write per chunk
            mapping_col: Dictionary of column mappings
            
        Returns:
            bool: True if write was successful
        """

        assert mode in ["fail", "append", "overwrite"], "Invalid mode"
        if mode == 'overwrite':
            engine = self.create_sqlalchemy_engine(source=dest, database=database)
            with engine.connect() as conn:
                table_name = '.'.join(table.split(".")[-2:])
                conn.execute(text(f"TRUNCATE TABLE nessie.{table_name}"))
                conn.commit()
        try:
            # Create SQLAlchemy engine
            engine = self.create_sqlalchemy_engine(source=dest, database=database)
            if dest is None:
                schema, table = table.split(".")[-2:]
            else:
                schema = None
            
            # Apply column mapping if provided
            if mapping_col:
                for col in mapping_col.keys():
                    df = df.rename(columns={col: mapping_col[col]})
                df = df[list(mapping_col.values())]
            
            # Cast type

            dtype_mapping = {
                col: self.get_sqlalchemy_type(dtype) 
                for col, dtype in df.dtypes.items()
            }
            # Write to database
            df.to_sql(
                name=table,
                schema=schema,
                con=engine,
                if_exists='append',
                method=method,
                chunksize=chunk_size,
                dtype=dtype_mapping,
                index=index
            )
            logger.info(f"Successfully wrote data to {database}.{table}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing data to {database}.{table}: {str(e)}")
            raise

    def run_local_spark_job(
        self,
        code_fn: Union[str, Callable],
        executors: Dict[str, Union[int, float]] = {"cpu": 1, "mem": 1}
    ) -> Optional[dict]:
        """Run a Spark job locally with specified configuration
        
        Args:
            code_fn: Either a file path or a function containing the Spark code
            executors: Dictionary with executor configuration:
                - cpu: CPU cores per executor
                - mem: Memory per executor in GB
        
        Returns:
            Dictionary containing job results if successful
        """
        spark = self.get_spark_session(config={"cores": executors["cpu"], "memory": f"{executors['mem']}g"})
        return code_fn(spark, self)

    def get_variable_value(self, code: str) -> str:
        """Get variable value by code."""
        return self._credentials.get_variable_value(code)
