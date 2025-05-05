"""
DuckDB connection and operations module.
"""
from typing import Optional, Dict, Any
import duckdb
from urllib.parse import urlparse

def get_duckdb_con(database: Optional[str] = None) -> duckdb.DuckDBPyConnection:
    """
    Get a DuckDB connection.
    
    Args:
        database: Optional path to a database file (default: in-memory)
        
    Returns:
        DuckDB connection object
    """
    con = duckdb.connect(database=database)
    _setup_extensions(con)
    return con

def _setup_extensions(con: duckdb.DuckDBPyConnection):
    """Setup required DuckDB extensions."""
    extensions = [
        "iceberg",
        "httpfs",
        "parquet"
    ]
    
    for ext in extensions:
        con.install_extension(ext)
        con.load_extension(ext)
    
    # Configure S3 settings
    con.sql("""
        SET s3_endpoint='localhost:9000';
        SET s3_access_key_id='admin';
        SET s3_secret_access_key='password';
        SET s3_use_ssl=false;
    """)

def attach_database_to_duckdb(source: str, db_source: str, db_dest: str,
                            con: Optional[duckdb.DuckDBPyConnection] = None) -> None:
    """
    Attach an external database to DuckDB.
    
    Args:
        source: Source connection string (e.g., 'postgres://user:pass@host:port/db')
        db_source: Source database name
        db_dest: Destination database name in DuckDB
        con: Optional DuckDB connection (creates new if None)
    """
    if con is None:
        con = get_duckdb_con()
        
    parsed = urlparse(source)
    source_type = parsed.scheme
    
    if source_type == 'postgres':
        con.sql(f"""
            ATTACH '{source}' AS {db_dest} (TYPE postgres);
            USE {db_dest};
        """)
    elif source_type == 'mysql':
        con.sql(f"""
            ATTACH '{source}' AS {db_dest} (TYPE mysql);
            USE {db_dest};
        """)
    else:
        raise ValueError(f"Unsupported database type: {source_type}")

def attach_files_to_duckdb(source: str, file_type: str, path: str, tbl_dest: str,
                          con: Optional[duckdb.DuckDBPyConnection] = None) -> None:
    """
    Attach external files to DuckDB.
    
    Args:
        source: Source type (s3, local, web)
        file_type: File type (csv, json, parquet)
        path: Path to the files
        tbl_dest: Destination table name in DuckDB
        con: Optional DuckDB connection (creates new if None)
    """
    if con is None:
        con = get_duckdb_con()
        
    if source.startswith('s3'):
        path = f"s3://{path.lstrip('/')}"
    elif source.startswith('web'):
        path = f"http://{path.lstrip('/')}"
        
    if file_type == 'csv':
        con.sql(f"CREATE TABLE {tbl_dest} AS SELECT * FROM read_csv('{path}')")
    elif file_type == 'json':
        con.sql(f"CREATE TABLE {tbl_dest} AS SELECT * FROM read_json('{path}')")
    elif file_type == 'parquet':
        con.sql(f"CREATE TABLE {tbl_dest} AS SELECT * FROM read_parquet('{path}')")
    else:
        raise ValueError(f"Unsupported file type: {file_type}") 