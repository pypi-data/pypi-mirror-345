"""
Module for managing database credentials and connections.
"""
import os
from typing import Dict, Any, Optional
import logging
import requests
import yaml  # Add yaml import

logger = logging.getLogger(__name__)

class CredentialsManager:
    """Manages database credentials and connection information."""
    
    USER_TOKEN = os.environ.get("USER_TOKEN", "")
    API_URL_BASE = os.environ.get("API_URL_BASE", "https://dev-sdk.ird.vng.vn/v1/sources/")
    
    def __init__(self):
        """Initialize credentials manager."""
        self._credentials = {}
    
    def get_credentials_by_code(self, alias: str= None) -> Dict[str, Any]:
        """Get credentials by source code."""
        if not self.USER_TOKEN:
            raise Exception("USER_TOKEN environment variable is not set")

        # Ensure API URL ends with /
        api_url = self.API_URL_BASE
        if not api_url.endswith("/"):
            api_url += "/"
        api_url += "detail"

        # Make POST request to detail endpoint

        if not alias:
            return {"host": "trino.ird.vng.vn", "port": 8443, "username": "trino", "password": "gwu8TXB9mbu9mda_nmx", "catalog": "nessie"}

        try:
            # Remove any leading/trailing whitespace and ensure proper format
            alias = alias.strip()
            
            # # If alias is just a name (e.g., "PGIRD"), prepend the type
            # if "/" not in alias:
            #     raise Exception("Source code must be in format 'type/name' (e.g., 'postgresql/PGIRD')")
            
            response = requests.post(
                api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.USER_TOKEN}"
                },
                json={"code": alias},
                verify=False  # Skip SSL verification
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
            try:
                response_data = response.json()
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response.text}")
                raise Exception("Invalid JSON response from API")
                
            if not isinstance(response_data, dict):
                raise Exception("Invalid response format: expected dictionary")
                
            if "success" not in response_data or response_data["success"] != 1:
                raise Exception(f"API request was not successful: {response_data.get('message', 'Unknown error')}")
                
            if "data" not in response_data:
                raise Exception("Missing 'data' field in response")
                
            if not isinstance(response_data["data"], dict):
                raise Exception("Invalid 'data' field: expected dictionary")
                
            if "information" not in response_data["data"]:
                raise Exception("Missing 'information' field in data")
                
            if not isinstance(response_data["data"]["information"], dict):
                raise Exception("Invalid 'information' field: expected dictionary")
                
            info = response_data["data"]["information"]
            
            # Check if this is a Google Sheets source
            if alias.startswith("google_sheet/"):
                return {
                    "info": info.get("info", {})
                }
            
            # For other sources, map API fields to expected fields
            return {
                "host": info["host"],
                "port": info["port"],
                "username": info["username"],
                "password": info["password"],
                "database": info.get("database_name", "postgres"),
                "info": info.get("info", {})
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting credentials: {e}")
            raise


    def get_variable_value(self, code: str) -> str:
        """Get variable value by code."""
        url = self.API_URL_BASE.replace("sources", "variables") + "value"
        response = requests.post(
            url,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.USER_TOKEN}"},
            json={"code": code}
        )
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")

        if response.json()["success"] != 1:
            raise Exception(response.json()["message"])
            
        data = response.json()["data"]
        if data["format"] == "text":
            return data["value"]
        elif data["format"] == "json":
            return data["value"]
        elif data["format"] == "yaml":
            try:
                # Parse YAML string into Python object
                yaml_data = yaml.safe_load(data["value"])
                return yaml_data
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse YAML: {e}")
                raise Exception(f"Invalid YAML format: {str(e)}")
        else:
            raise Exception(f"Variable value format {data['format']} is not supported")

    def get_jdbc_credentials(self, source: str, database: str) -> str:
        """Get JDBC credentials by source ID."""
        try:
            if not source:
                raise Exception("Source code cannot be None or empty")
                
            creds = self.get_credentials_by_code(source)
            if not creds:
                raise Exception(f"No credentials found for source {source}")
            
            # Extract required fields
            host = creds.get('host')
            port = creds.get('port')
            user = creds.get('username')
            password = creds.get('password')
            
            if not all([host, port, user, password]):
                raise Exception("Missing required credentials fields")
            
            # Determine database type from source code
            db_type = source.split('/')[0].lower()
            
            if db_type == "postgresql":
                # Format PostgreSQL JDBC URL with SSL disabled
                return f"jdbc:postgresql://{host}:{port}/{database}?user={user}&password={password}&ssl=false"
            elif db_type == "mysql":
                # Format MySQL JDBC URL with additional parameters
                return f"jdbc:mysql://{host}:{port}/{database}?user={user}&password={password}&useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC"
            else:
                raise Exception(f"Unsupported database type: {db_type}")
                
        except Exception as e:
            logger.error(f"Error getting JDBC credentials: {e}")
            raise
    
    def get_nessie_credentials(self, source_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get Nessie credentials by source ID."""
        if source_id is None:
            source_id = "nessie_source:default"
        if not source_id.startswith("nessie_source:"):
            source_id = f"nessie_source:{source_id}"
        return self._credentials.get(source_id)
    
    
    def validate_nessie_connection(self, source_id: Optional[str] = None) -> bool:
        """
        Validate Nessie connection using stored credentials.
        
        Args:
            source_id: Optional source ID. If None, validates default credentials
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        creds = self.get_nessie_credentials(source_id)
        if not creds:
            return False
            
        try:
            # Basic validation of required fields
            required_fields = ['uri', 'ref', 'warehouse', 'io_impl']
            return all(field in creds for field in required_fields)
        except Exception:
            return False