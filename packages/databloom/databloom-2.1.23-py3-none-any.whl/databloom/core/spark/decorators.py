"""
Decorators for Spark functionality.
"""
from functools import wraps
from typing import Optional, Callable, Any
from pyspark.sql.types import DataType

def spark_udf(name: Optional[str] = None, return_type: Optional[DataType] = None):
    """
    Decorator to mark a function as a Spark UDF.
    
    This decorator marks a Python function to be registered as a Spark UDF
    when used with run_spark_job. The function can specify its return type
    and custom name for registration.
    
    Args:
        name: Optional name for the UDF. If not provided, function name will be used.
        return_type: Optional return type for the UDF (e.g., StringType(), IntegerType())
        
    Returns:
        Decorated function
        
    Example:
        @spark_udf(return_type=StringType())
        def my_udf(x):
            return str(x).upper()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Execute the original function directly
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error in UDF execution: {e}")
                raise
            
        # Mark function as UDF and store metadata
        wrapper._is_udf = True
        wrapper._udf_name = name or func.__name__
        wrapper._return_type = return_type
        wrapper._original_func = func
        
        return wrapper
        
    return decorator 