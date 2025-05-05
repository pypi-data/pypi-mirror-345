"""
Spark session management for DataBloom SDK.
"""
import os
import logging
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from typing import Dict

logger = logging.getLogger(__name__)

class SparkSessionManager:
    """Manager class for Spark session."""
    
    def __init__(self):
        """Initialize Spark session manager."""
        self._session = None
        
    def get_session(self, app_name: str = "DataBloom", config: Dict[str, str] = {"cores": 1, "memory": "1g"}, mode: str = "local") -> SparkSession:
        """
        Get or create a Spark session.
        
        Args:
            app_name: Name for the Spark application
            
        Returns:
            SparkSession instance
        """
        if not self._session:
            try:
                # Get environment variables
                nessie_uri = os.getenv("NESSIE_URI", "http://49.213.85.108:19120/iceberg/main")
                
                # Create Spark session builder with packages
                packages = [
                    # Postgresql
                    "org.postgresql:postgresql:42.2.5",
                    # MySQL
                    "mysql:mysql-connector-java:8.0.28"
                ]
                
                # Add Nessie packages if URI is configured
                if nessie_uri:
                    packages.extend([
                        "org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.99.0",
                        "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.0",
                        "software.amazon.awssdk:bundle:2.28.17",
                        "software.amazon.awssdk:url-connection-client:2.28.17"
                    ])
                
                # Create Spark configuration
                conf = SparkConf()
                conf.set("spark.app.name", app_name)
                if mode == "local":
                    conf.set("spark.master", "local[*]")
                conf.set("spark.jars.packages", ",".join(packages))
                
                # Add Nessie configuration if URI is configured
                if nessie_uri:
                    conf.set("spark.sql.extensions", 
                            "org.projectnessie.spark.extensions.NessieSparkSessionExtensions,org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
                    conf.set("spark.sql.catalog.nessie", "org.apache.iceberg.spark.SparkCatalog")
                    conf.set("spark.sql.catalog.nessie.type", "rest")
                    conf.set("spark.sql.catalog.nessie.uri", nessie_uri)
                    conf.set("spark.sql.catalogImplementation", "in-memory")
                    conf.set("spark.driver.cores", config["cores"])
                    conf.set("spark.driver.memory", config["memory"])
                
                # Create session
                self._session = SparkSession.builder \
                    .config(conf=conf) \
                    .getOrCreate()
                self._session.sparkContext.setLogLevel("WARN")
                
                # Create default namespace if Nessie is configured
                if nessie_uri:
                    try:
                        self._session.sql("CREATE NAMESPACE IF NOT EXISTS nessie.default")
                        logger.info("Default namespace created or already exists")
                    except Exception as e:
                        logger.warning(f"Failed to create default namespace: {e}")
                
                logger.info("Successfully created Spark session")
                
            except Exception as e:
                logger.error(f"Failed to create Spark session: {e}")
                raise
                
        return self._session
        
    def stop_session(self):
        """Stop the Spark session if it exists."""
        if self._session:
            try:
                self._session.stop()
                self._session = None
                logger.info("Successfully stopped Spark session")
            except Exception as e:
                logger.error(f"Failed to stop Spark session: {e}")
                raise 