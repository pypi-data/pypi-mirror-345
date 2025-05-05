"""
Module for metadata operations in DataBloom SDK.
"""
import logging
import requests
from typing import Dict, Optional
from .api.nessie_metadata import NessieMetadataClient

logger = logging.getLogger(__name__)

def get_s3_metadata(table_name: str,
                   namespace: str = "default",
                   nessie_url: str = "http://localhost:19120/api/v1") -> str:
    """Get the S3 metadata location for a table in the Nessie catalog.
    
    Args:
        table_name: Name of the table (e.g. 'category_table_v2')
        namespace: Namespace containing the table (default: 'default')
        nessie_url: Base URL for Nessie API
        
    Returns:
        str: S3 path to the metadata file
        
    Raises:
        ValueError: If table is not found or metadata location is invalid
    """
    try:
        # Make request to Nessie API
        full_table_name = f"{namespace}.{table_name}"
        url = f"{nessie_url}/contents/{full_table_name}"
        
        response = requests.get(url)
        if response.status_code == 404:
            raise ValueError(f"Table {full_table_name} not found")
        response.raise_for_status()
        
        data = response.json()
        metadata_location = data.get('metadataLocation')
        if not metadata_location:
            raise ValueError("No metadata location found in API response")
            
        # Normalize S3 path
        if metadata_location.startswith('s3a://'):
            metadata_location = 's3://' + metadata_location[6:]
        elif not metadata_location.startswith('s3://'):
            metadata_location = 's3://' + metadata_location
            
        return metadata_location
        
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            raise ValueError(f"Table {full_table_name} not found")
        raise ValueError(f"Error connecting to Nessie API: {e}")

def find_metadata(table_name: str,
                 namespace: str = "default",
                 nessie_url: str = "http://localhost:19120/api/v1",
                 ref: str = "main",
                 s3_endpoint: str = "http://localhost:9000",
                 s3_access_key: str = "admin",
                 s3_secret_key: str = "password") -> Dict:
    """Find metadata for a table in the Nessie catalog.
    
    This function provides a simple interface to find metadata for a table,
    including its schema, location, and other properties.
    
    Args:
        table_name: Name of the table (e.g. 'category_table_v2')
        namespace: Namespace containing the table (default: 'default')
        nessie_url: Base URL for Nessie API
        ref: Reference (branch/tag) to use
        s3_endpoint: S3 endpoint for accessing metadata files
        s3_access_key: S3 access key
        s3_secret_key: S3 secret key
        
    Returns:
        Dict containing table metadata including:
            - table_uuid: Unique identifier for the table
            - location: S3 location of the table data
            - last_updated_ms: Last update timestamp
            - schema: Current schema definition
            - properties: Table properties
            - current_snapshot: Latest snapshot information
            - partition_specs: Partitioning specifications
            - sort_orders: Sort order specifications
            
    Raises:
        ValueError: If table is not found or metadata is invalid
        Exception: For other errors (e.g. connection issues)
    """
    try:
        # Initialize the Nessie client
        client = NessieMetadataClient(
            nessie_url=nessie_url,
            ref=ref,
            s3_endpoint=s3_endpoint,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key
        )
        
        # Find metadata using the client
        logger.info(f"Finding metadata for table '{table_name}' in namespace '{namespace}'")
        metadata = client.find_table_metadata(table_name, namespace)
        
        # Log some useful information
        logger.info(f"Found table UUID: {metadata['table_uuid']}")
        logger.info(f"Table location: {metadata['location']}")
        logger.info(f"Last updated: {metadata['last_updated_ms']}")
        logger.info(f"Number of fields: {len(metadata['schema']['fields'])}")
        
        return metadata
        
    except ValueError as e:
        logger.error(f"Invalid table or metadata: {e}")
        raise
    except Exception as e:
        logger.error(f"Error finding metadata: {e}")
        raise 