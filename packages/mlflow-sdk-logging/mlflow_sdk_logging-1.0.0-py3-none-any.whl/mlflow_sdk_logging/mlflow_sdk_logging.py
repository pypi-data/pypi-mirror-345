import mlflow
import os
import logging
from datetime import datetime
 
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
 
class MLflowLogger:
    def __init__(self, experiment_name, run_name=None):
        self.experiment_name = experiment_name
        self.run_name = run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.run = None
 
    def __enter__(self):
        # Set tracking URI from environment
        uri = os.environ.get("MLFLOW_TRACKING_URI")
        if not uri:
            logging.error("Environment variable 'MLFLOW_TRACKING_URI' is not set. Cannot proceed.")
            raise EnvironmentError("MLFLOW_TRACKING_URI is not set")
        mlflow.set_tracking_uri(uri)
 
        logging.info(f"Using MLFLOW_TRACKING_URI: {uri}")
        mlflow.set_experiment(self.experiment_name)
        self.run = mlflow.start_run(run_name=self.run_name)
        logging.info(f"Started MLflow run with ID: {self.run.info.run_id}")
        return self
 
    def log_param(self, param_name, param_value):
        mlflow.log_param(param_name, param_value)
        logging.info(f"Logged param: {param_name} = {param_value}")
 
    def log_metric(self, metric_name, metric_value):
        mlflow.log_metric(metric_name, metric_value)
        logging.info(f"Logged metric: {metric_name} = {metric_value}")
 
    def log_artifact(self, artifact_path):
        if os.path.exists(artifact_path):
            if os.path.isdir(artifact_path):
                for root, _, files in os.walk(artifact_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, artifact_path)
                        mlflow.log_artifact(file_path, artifact_path=os.path.dirname(relative_path))
            else:
                mlflow.log_artifact(artifact_path)
            logging.info(f"Logged artifact: {artifact_path}")
        else:
            logging.warning(f"Artifact path '{artifact_path}' does not exist.")
 
    def __exit__(self, exc_type, exc_value, traceback):
        mlflow.end_run()
        logging.info("MLflow run ended.")