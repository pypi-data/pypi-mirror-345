import os
import gspread
import pandas as pd
import json
from google.oauth2.credentials import Credentials
from databloom.api.credentials import CredentialsManager
import logging

logger = logging.getLogger(__name__)

def get_ggsheet_client(source: str):
    """Get authenticated Google Sheets client.
    
    Args:
        source: Source identifier in format 'google_sheet/name'
        
    Returns:
        gspread.client.Client: Authenticated Google Sheets client
    """
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        # Get credentials from DataBloom context
        creds_info = CredentialsManager().get_credentials_by_code(source)
        logger.info(f"Received credentials for source: {source}")
        
        # Extract auth token from info
        auth_token = creds_info.get("info", {}).get("auth_token")
        if not auth_token:
            raise ValueError(f"No auth token found in credentials for source: {source}")
            
        # Parse the auth token JSON
        try:
            token_data = json.loads(auth_token)
            logger.info("Successfully parsed auth token")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse auth token: {e}")
            raise
            
        # Write token to /tmp/token.json
        token_json = json.dumps(token_data)
        with open("/tmp/token.json", "w") as f:
            f.write(token_json)
        logger.info("Successfully wrote token file")
        
        # Create credentials from token file
        creds = Credentials.from_authorized_user_file("/tmp/token.json", SCOPES)
        logger.info("Successfully created credentials")
        
        # Authorize client
        client = gspread.authorize(creds)
        logger.info("Successfully authorized client")
        return client
        
    except Exception as e:
        logger.error(f"Error getting Google Sheets client: {e}")
        raise

def read_ggsheet(source: str, sheet: str, worksheetname: str) -> pd.DataFrame:
    """Read data from Google Sheet.
    
    Args:
        source: Source identifier in format 'google_sheet/name'
        sheet: Name of the Google Sheet
        worksheetname: Name of the worksheet within the sheet
        
    Returns:
        pd.DataFrame: Data from the Google Sheet
    """
    try:
        # Get authenticated client
        client = get_ggsheet_client(source)
        logger.info(f"Opening sheet: {sheet}, worksheet: {worksheetname}")
        
        # Open the specified sheet and worksheet
        sheet = client.open(sheet).worksheet(worksheetname)
        
        # Read data from sheet
        data = sheet.get_all_values()
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Use first row as headers
            df.columns = df.iloc[0]
            df = df[1:]
            logger.info(f"Successfully read {len(df)} rows from sheet")
            return df
        else:
            logger.warning("No data read from sheet")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Error reading Google Sheet: {e}")
        raise 