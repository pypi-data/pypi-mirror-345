#!/usr/bin/env python3
import os
import requests
import json
import time
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Union, Callable
import inspect
import random
import re


def process_result(result, verbose=False):
    """Process the result of a Spark job execution."""
    try:
        # Check if result is None
        if result is None:
            print("No result data found")
            return None

        # Print raw output for debugging
        if verbose:
            print("\nRaw output data:")
            print(result)
        # Extract output data from Livy response
        if not isinstance(result, dict):
            return None
            
        output = result.get('output', {})
        if not output or not isinstance(output, dict):
            return None
            
        data = output.get('data', {})
        if not data or not isinstance(data, dict):
            return None
            
        text_data = data.get('text/plain', '')
        if not text_data:
            return None
            
        # Look for "Function result:" in the output
        result_marker = "Function result:"
        if result_marker in text_data:
            try:
                result_json = text_data[text_data.index(result_marker) + len(result_marker):].strip()
                parsed = json.loads(result_json)
                
                # Handle pandas DataFrame case
                if isinstance(parsed, dict) and 'pandas_dataframe' in parsed:
                    df_dict = parsed['pandas_dataframe']
                    return pd.DataFrame(df_dict['data'], columns=df_dict['columns'])
                
                # Handle list of dictionaries case (DataFrame-like)
                if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
                    return pd.DataFrame(parsed)
                    
                # Handle list of lists case (DataFrame-like with no column names)
                if isinstance(parsed, list) and parsed and isinstance(parsed[0], list):
                    return pd.DataFrame(parsed)
                
                # Handle dictionary with 'records' key
                if isinstance(parsed, dict) and 'records' in parsed:
                    return pd.DataFrame(parsed['records'])
                    
                # Handle regular dictionary
                if isinstance(parsed, dict):
                    return pd.DataFrame([parsed])
                    
            except json.JSONDecodeError:
                pass

        # Try to find any JSON array in the output as fallback
        try:
            matches = re.findall(r'\[.*?\]', text_data, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, list) and parsed:
                        # Handle list of dictionaries
                        if isinstance(parsed[0], dict):
                            return pd.DataFrame(parsed)
                        # Handle list of lists
                        elif isinstance(parsed[0], list):
                            return pd.DataFrame(parsed)
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            print(f"Error parsing JSON from text: {e}")

        return None

    except Exception as e:
        print(f"Error processing result: {e}")
        import traceback
        print(f"Full traceback:\n{traceback.format_exc()}")
        return None

def convert_to_dataframe(result, verbose=False):
    """Convert the result to a pandas DataFrame."""
    result = process_result(result, verbose=verbose)
    try:
        if result is None:
            return None
        return pd.DataFrame(result)
    except:
        return None

class LighterContext:
    def __init__(self, verbose=False, lighter_api_url: str = "https://dev-sdk.ird.vng.vn/v1/sources/"):
        """Initialize LighterContext with API URL and namespace
        
        Args:
            verbose (bool): Enable verbose logging
            base_url (str): Base URL for the Lighter API
        """
        self.base_url = os.getenv("LIGHTER_API_URL", lighter_api_url)
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-Compatibility-Mode": "sparkmagic"
        })
        # Add retry logic
        retry_strategy = requests.adapters.Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.verbose = verbose
        if self.verbose:
            print("Initialized LighterContext with:")
            print(f"  Base URL: {self.base_url}")
            print(f"  Headers: {json.dumps(dict(self.session.headers), indent=2)}")
    
    def _log(self, message, always_print=False):
        """Log message if verbose is enabled or if always_print is True"""
        if self.verbose or always_print:
            print(message)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to Lighter API"""
        url = f"{self.base_url}/{endpoint}"
        self._log(f"\nMaking {method} request to: {url}", not endpoint.startswith("sessions/") or self.verbose)
        self._log(f"Headers: {self.session.headers}")
        if ('json' in kwargs) and self.verbose:
            self._log(f"Request data: {json.dumps(kwargs['json'], indent=2)}", True)
        
        try:
            # Add timeout to request
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 30
            response = self.session.request(method, url, **kwargs)
            if self.verbose:
                self._log(f"Response status: {response.status_code}", not endpoint.startswith("sessions/") or self.verbose)
                self._log(f"Response headers: {dict(response.headers)}")
                self._log(f"Response content: {response.text}")
            
            response.raise_for_status()
            return response.json() if response.content else None
            
        except requests.exceptions.RequestException as e:
            self._log(f"\nError making request:", True)
            self._log(f"  URL: {url}", True)
            self._log(f"  Method: {method}", True)
            self._log(f"  Error: {str(e)}", True)
            if hasattr(e, 'response') and e.response is not None:
                self._log(f"  Status code: {e.response.status_code}", True)
                self._log(f"  Response headers: {dict(e.response.headers)}", True)
                self._log(f"  Response content: {e.response.text}", True)
            raise

    def _create_session(self, executors=None, env_vars={}):
        """Create a new Spark session"""
        if executors is None:
            executors = {"num_executors": 4, "cpu": 1, "mem": 1}
            
        spark_packages = [
            "org.postgresql:postgresql:42.2.5",
            "mysql:mysql-connector-java:8.0.28",
            "org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.99.0",
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.0",
            "software.amazon.awssdk:bundle:2.28.17",
            "software.amazon.awssdk:url-connection-client:2.28.17"
        ]

        config = {
            "kind": "pyspark",
            "name": "PySpark Job",
            "conf": {
                "spark.kubernetes.container.image": "registry.ird.vng.vn/databloom/databloom-worker:2.1.9",
                # "spark.kubernetes.container.image": "registry.ird.vng.vn/databloom/databloom-worker:latest",
                "spark.kubernetes.authenticate.driver.serviceAccountName": "default",
                "spark.kubernetes.container.image.pullPolicy": "Always",
                "spark.kubernetes.container.image.pullSecrets": "harbor-registry",
                "spark.kubernetes.driver.container.image.pullSecrets": "harbor-registry",
                "spark.kubernetes.executor.container.image.pullSecrets": "harbor-registry",
                "spark.executor.instances": str(executors["num_executors"]),
                "spark.executor.memory": f"{executors['mem']}g",
                "spark.executor.cores": str(executors["cpu"]),
                "spark.driver.memory": "1g",
                "spark.driver.cores": "1",
                "spark.kubernetes.namespace": "namvq",
                "spark.dynamicAllocation.enabled": "false",
                # "spark.jars.packages" : ",".join(spark_packages),
                "spark.driver.extraClassPath": "/opt/spark/jars/*",
                "spark.executor.extraClassPath": "/opt/spark/jars/*",
                "spark.sql.extensions": "org.projectnessie.spark.extensions.NessieSparkSessionExtensions,org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
                "spark.sql.catalog.nessie": "org.apache.iceberg.spark.SparkCatalog",
                "spark.sql.catalog.nessie.type": "rest",
                "spark.sql.catalog.nessie.uri": os.getenv("NESSIE_URI", "http://49.213.85.108:19120/iceberg/main"),
                "spark.sql.catalogImplementation": "in-memory"
            }
        }
        # Add environment variables if provided
        if env_vars:
            # Add each environment variable individually
            for key, value in env_vars.items():
                # For driver
                config["conf"][f"spark.kubernetes.driverEnv.{key}"] = value
                # For executor
                config["conf"][f"spark.executorEnv.{key}"] = value
                # Also add as a Spark configuration
                config["conf"][f"spark.{key}"] = value
        
        self._log("\nCreating new Spark session...")
        response = self._request("POST", "sessions", json=config)
        
        if not response or 'id' not in response:
            self._log("Failed to get session ID from response")
            self._log(f"Response: {response}")
            raise Exception("Failed to create session")
        
        session_id = response['id']
        self._log(f"Session created with ID: {session_id}")
        return session_id

    def _wait_for_session(self, session_id: str, timeout: int = 300) -> bool:
        """Wait for session to be ready"""
        self._log(f"\nWaiting for session {session_id} to be ready...", True)
        end_time = time.time() + timeout
        last_state = None
        
        while time.time() < end_time:
            try:
                session = self._request("GET", f"sessions/{session_id}")
                state = session.get("state", "").lower()
                
                # Only log state changes when not verbose
                if state != last_state:
                    self._log(f"Session state: {state}", True)
                    last_state = state
                
                self._log(f"Full session info: {json.dumps(session, indent=2)}")
                
                if state == "idle":
                    self._log("Session is ready", True)
                    return True
                if state in ["error", "dead", "killed"]:
                    self._log(f"Session failed with state: {state}", True)
                    self._log(f"Session details: {json.dumps(session, indent=2)}", True)
                    raise Exception(f"Session failed: {state}")
                
                if self.verbose:
                    self._log(f"Waiting for session... (state: {state})")
                time.sleep(5)
                
            except Exception as e:
                self._log(f"Error checking session state: {str(e)}", True)
                raise
        
        raise TimeoutError("Session startup timed out")
    
    def _wait_for_completion(self, session_id: str, statement_id: str, timeout: int = 300) -> dict:
        """Wait for statement execution to complete"""
        self._log(f"\nWaiting for statement {statement_id} to complete...", True)
        end_time = time.time() + timeout
        last_state = None
        
        while time.time() < end_time:
            try:
                result = self._request("GET", f"sessions/{session_id}/statements/{statement_id}")
                state = result.get("state", "").lower()
                
                # Only log state changes when not verbose
                if state != last_state:
                    self._log(f"Statement state: {state}", True)
                    last_state = state
                
                # Print output if available
                output = result.get("output", {})
                if output:
                    if output.get("status") == "error":
                        error_msg = f"Error: {output.get('ename')}: {output.get('evalue')}"
                        if output.get("traceback"):
                            error_msg += f"\nTraceback: {''.join(output['traceback'])}"
                        self._log(error_msg, True)
                        raise Exception(error_msg)
                    
                    data = output.get("data", {})
                    if data:
                        # Print text/plain output
                        if "text/plain" in data:
                            self._log(f"Output (text/plain):\n{data['text/plain']}", True)
                        # Print application/json output
                        if "application/json" in data:
                            self._log(f"Output (application/json):\n{json.dumps(data['application/json'], indent=2)}", True)
                
                if state == "available":
                    self._log("Statement completed successfully", True)
                    return result
                if state in ["error", "cancelled"]:
                    error_msg = "Statement failed"
                    if output and output.get("traceback"):
                        error_msg += f": {''.join(output['traceback'])}"
                    raise Exception(error_msg)
                
                if self.verbose:
                    self._log(f"Waiting for statement... (state: {state})")
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                self._log(f"Error checking statement state: {str(e)}", True)
                if hasattr(e, 'response') and e.response is not None:
                    self._log(f"Response status: {e.response.status_code}", True)
                    self._log(f"Response content: {e.response.text}", True)
                raise
        
        raise TimeoutError("Statement execution timed out")

    def run_spark_job(
        self,
        code_fn: Union[str, Callable],
        mode: str = "cluster",
        executors: Dict[str, Union[int, float]] = {"num_executors": 2, "cpu": 1, "mem": 1}
    ) -> Optional[dict]:
        """Run a Spark job with specified configuration
        
        Args:
            code_fn: Either a file path or a function containing the Spark code
            mode: Execution mode ("cluster" or "client")
            executors: Dictionary with executor configuration:
                - num_executors: Number of executors
                - cpu: CPU cores per executor
                - mem: Memory per executor in GB
        
        Returns:
            Dictionary containing job results if successful
        """
        if mode not in ["cluster", "client"]:
            raise ValueError("Mode must be either 'cluster' or 'client'")

        if mode == "client":
            return self.run_spark_job_local(code_fn, executors)

        try:
            # Create session
            self._log(f"Creating Spark session with {executors['num_executors']} executors...")
            env_vars={
                "USER_TOKEN": os.environ.get("USER_TOKEN"),
                "API_URL_BASE": os.environ.get("API_URL_BASE"),
                "NESSIE_URI": os.environ.get("NESSIE_URI")
            }
            session_id = self._create_session(executors, env_vars)
            
            # Wait for session to be ready
            self._wait_for_session(session_id)
            
            # Handle code based on type
            if callable(code_fn):
                # Get function source
                code = inspect.getsource(code_fn)
                
                # Create a temporary file with the code
                tmp_file = Path(f"/tmp/{session_id}.py")
                
                # Write the code to file
                with open(tmp_file, "w") as f:
                    # Write imports and setup
                    f.write("#!/usr/bin/env python3\n")
                    f.write("import json\n")

                    f.write("from databloom import DataBloomContext\n")
                    f.write("dc = DataBloomContext()\n")
                    f.write("spark = dc.get_spark_session()\n")
                    # Write the function definition
                    f.write(code)
                    f.write("\n\n")
                    
                    # Write the function call
                    f.write("# Call the function and print result\n")
                    # f.write(f"result = {code_fn.__name__}(spark, ctx)\n")
                    f.write(f"result = {code_fn.__name__}(spark=spark, dc=dc)\n")
                    # if result is a pandas DataFrame, then convert it to a dict
                    f.write("import pandas as pd\n")
                    f.write("if isinstance(result, pd.DataFrame):\n")
                    f.write("    result = result.to_dict(orient='records')\n")
                    f.write("print(\"\\nFunction result:\", json.dumps(result, indent=2))\n")
                    
                
                self._log(f"Writing code to temporary file: {tmp_file}")
                self._log("Code written to file:")
                self._log("-" * 40)
                with open(tmp_file, "r") as f:
                    self._log(f.read())
                self._log("-" * 40)
                
                # Submit code
                self._log("\nSubmitting code...")
                with open(tmp_file, "r") as f:
                    statement = self._request("POST", f"sessions/{session_id}/statements", json={
                        "code": f.read(),
                        "kind": "pyspark"
                    })
                
                # Wait for completion
                result = self._wait_for_completion(session_id, statement["id"])
                
                # Clean up
                self._log("Cleaning up session...")
                tmp_file.unlink()
                self._log(f"Removed temporary file: {tmp_file}")
                
                # Delete session
                self._request("DELETE", f"sessions/{session_id}")
                self._log("Session cleaned up\n")
                
                rs_type_df = convert_to_dataframe(result, verbose=self.verbose)
                return rs_type_df
                
            else:
                # Handle file path
                code_path = Path(code_fn)
                if not code_path.exists():
                    raise FileNotFoundError(f"Code file not found: {code_path}")
                
                with open(code_path, "r") as f:
                    statement = self._request("POST", f"sessions/{session_id}/statements", json={
                        "code": f.read(),
                        "kind": "pyspark"
                    })
                
                return self._wait_for_completion(session_id, statement["id"])
                
        except Exception as e:
            self._log(f"\nError in run_spark_job: {str(e)}", True)
            import traceback
            self._log(f"Full traceback:\n{traceback.format_exc()}", True)
            # Delete the batch job if it exists
            if 'session_id' in locals():
                try:
                    self._log(f"Deleting batch job with session ID: {session_id}", True)
                    self._request("DELETE", f"sessions/{session_id}")
                    self._log("Batch job deleted successfully", True)
                except Exception as delete_error:
                    self._log(f"Failed to delete batch job: {str(delete_error)}", True)
            raise

    def run_spark_job_local(
        self,
        code_fn: Union[str, Callable],
        executors: Dict[str, Union[int, float]] = {"cpu": 1, "mem": 1}
    ) -> Optional[dict]:
        """Run a Spark job with specified configuration
        
        Args:
            code_fn: Either a file path or a function containing the Spark code
            executors: Dictionary with executor configuration:
                - num_executors: Number of executors
                - cpu: CPU cores per executor
                - mem: Memory per executor in GB
        
        Returns:
            Dictionary containing job results if successful
        """
        from databloom.core.databloom_context import DataBloomContext
        dc = DataBloomContext()
        return dc.run_local_spark_job(code_fn, executors)