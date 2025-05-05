"""
Module for data warehouse operations in DataBloom SDK.
"""
import os
import logging
from typing import Dict, Any, List
import boto3

logger = logging.getLogger(__name__)

class WarehouseManager:
    """Manager class for data warehouse operations."""
    
    def __init__(self):
        """Initialize warehouse manager."""
        self.s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('S3_ENDPOINT', 'http://localhost:9000'),
            aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID', 'admin'),
            aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY', 'password'),
            region_name='us-east-1'
        )
        
    def list_warehouse_contents(self, bucket: str = "nessie", prefix: str = "default/") -> Dict[str, Any]:
        """
        List contents of the data warehouse.
        
        Args:
            bucket: S3 bucket name
            prefix: Path prefix in bucket
            
        Returns:
            Dict containing listing results
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix
            )
            return response
        except Exception as e:
            logger.error(f"Failed to list warehouse contents: {str(e)}")
            raise
            
    def get_table_data_files(self, table_name: str, bucket: str = "nessie", prefix: str = "default/") -> List[Dict[str, Any]]:
        """
        Get data files for a specific table.
        
        Args:
            table_name: Name of the table
            bucket: S3 bucket name
            prefix: Path prefix in bucket
            
        Returns:
            List of data file information
        """
        try:
            # List objects with table prefix
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=f"{prefix}{table_name}"
            )
            
            # Filter data files
            data_files = []
            for obj in response.get('Contents', []):
                if '/data/' in obj['Key'] and obj['Key'].endswith('.parquet'):
                    data_files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat()
                    })
            
            return data_files
        except Exception as e:
            logger.error(f"Failed to get table data files: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    manager = WarehouseManager()
    
    # List warehouse contents
    contents = manager.list_warehouse_contents()
    print("\nWarehouse contents:")
    for item in contents.get('Contents', []):
        print(f"- {item['Key']}")
        
    # Get data files for category_table_v2
    data_files = manager.get_table_data_files("category_table_v2")
    print("\nData files:")
    for file in data_files:
        print(f"- {file['key']} ({file['size']} bytes, last modified: {file['last_modified']})") 