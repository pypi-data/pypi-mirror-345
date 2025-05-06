"""
DataBloom SDK for data integration.
"""

from .metadata import get_s3_metadata
from .dataset.dataset import Dataset
from .core.context import DataBloomContext
from .core.spark.decorators import spark_udf
from .version import __version__
from typing import Optional, Dict, Any, List, Callable
import pandas as pd
import re
import duckdb
from .api.nessie_metadata import NessieMetadataClient
from .api.credentials import CredentialsManager
from .core.connector.mysql import MySQLConnector
from .core.connector.postgresql import PostgreSQLConnector
from .core.connector.spark_postgresql import SparkPostgreSQLConnector
import logging
import os
from sqlalchemy import create_engine as sqlalchemy_create_engine
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from .core.spark.session import SparkSessionManager
import pyspark
from typing import Optional

__all__ = [
    'get_s3_metadata',
    'Dataset',
    'DataBloomContext',
    'run_spark_job',
    'spark_udf',
    '__version__'
]

logger = logging.getLogger(__name__)

def run_spark_job(func: Callable, mode: str = 'local', **kwargs) -> Any:
    """
    Run a Spark job with the given function.
    
    This function initializes a Spark session and applies the given function as a UDF job.
    The function can be either a regular Python function or a UDF-decorated function.
    
    Args:
        func: Python function to execute as a Spark job
        mode: Execution mode ('local' or 'cluster')
        **kwargs: Additional arguments passed to the function
        
    Returns:
        Result of the function execution
        
    Example:
        @spark_udf()
        def my_function(x):
            return x * 2
            
        result = run_spark_job(my_function, mode='local')
    """
    spark_manager = None
    try:
        # Create Spark session manager
        spark_manager = SparkSessionManager()
        
        # Configure session based on mode
        if mode == 'local':
            spark = spark_manager.get_session(app_name=f"SparkJob_{func.__name__}")
            spark.sparkContext.setLogLevel("WARN")  # Reduce logging noise
        else:
            raise ValueError(f"Unsupported mode: {mode}")
            
        # Handle UDF registration
        if hasattr(func, '_is_udf'):
            # Get the original function and metadata
            original_func = getattr(func, '_original_func', func)
            udf_name = getattr(func, '_udf_name', func.__name__)
            return_type = getattr(func, '_return_type', None)
            
            # Execute the function directly with provided arguments
            try:
                result = original_func(**kwargs)
                return result
            except Exception as e:
                logger.error(f"Error executing UDF function: {e}")
                raise
                
        elif isinstance(func, udf):
            # Function is already a PySpark UDF
            try:
                result = func(**kwargs)
                return result
            except Exception as e:
                logger.error(f"Error executing PySpark UDF: {e}")
                raise
                
        else:
            # Regular Python function
            try:
                result = func(**kwargs)
                return result
            except Exception as e:
                logger.error(f"Error executing Python function: {e}")
                raise
                
    except Exception as e:
        logger.error(f"Failed to execute Spark job: {e}")
        raise
    finally:
        if spark_manager:
            try:
                spark_manager.stop_session()
            except Exception as e:
                logger.warning(f"Error stopping Spark session: {e}")