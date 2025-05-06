import logging
import os

from importlib.util import spec_from_file_location, module_from_spec
from typing import Any

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class BaseTool:
    """
    Base class for all classes and tools that need to load settings.py and configure services.
    """

    def __init__(self, project_path: str) -> None:
        # Load the user's settings.py immediately
        self.settings: Any = self.load_project_settings(project_path)

        # If settings were successfully loaded, load services
        if self.settings:
            self.load_services()

    def load_project_settings(self, project_path: str) -> Any:
        """Dynamically load the correct settings.py from the user's project directory."""
        settings_path: str = os.path.join(project_path, "settings.py")

        if not os.path.exists(settings_path):
            logger.error(f"Error: settings.py not found at {settings_path}. Run `rae init` first.")
            return None

        # Load the settings.py file dynamically
        spec: Any = spec_from_file_location("settings", settings_path)
        if spec and spec.loader:
            settings_module: Any = module_from_spec(spec)
            spec.loader.exec_module(settings_module)
            logger.info(f"Successfully loaded settings from {settings_path}")
            return settings_module
        else:
            logger.error(f"Failed to load settings from {settings_path}")
            return None

    def load_services(self) -> Any:
        """Configure services using the loaded settings.py file."""
        if not self.settings:
            logger.error("Cannot load services because settings.py was not found.")
            return

        self.networks = getattr(self.settings, "NETWORKS", {"rae_network": {"driver": "bridge"}})
        self.project_name = getattr(self.settings, "PROJECT_NAME", "rae")
        self.volumes = getattr(self.settings, "VOLUMES", {})

        logger.info(f"Loaded Networks: {self.networks}")
        logger.info(f"Loaded Volumes: {self.volumes}")

        self.services = {}

        if hasattr(self.settings, "POSTGRES_DEFAULTS"):
            self.services[f"{self.project_name}_data_storage"] = self.settings.POSTGRES_DEFAULTS
            if hasattr(self.settings, "PGADMIN_DEFAULTS"):
                self.services[f"{self.project_name}_pgadmin"] = self.settings.PGADMIN_DEFAULTS
        elif hasattr(self.settings, "MYSQL_DEFAULTS"):
            self.services[f"{self.project_name}_data_storage"] = self.settings.MYSQL_DEFAULTS
            if hasattr(self.settings, "PHPMYADMIN_DEFAULTS"):
                self.services[f"{self.project_name}_phpmyadmin"] = self.settings.PHPMYADMIN_DEFAULTS

        if hasattr(self.settings, "AIRFLOW_METASTORE_DEFAULTS"):
            self.services[f"{self.project_name}_metastore"] = self.settings.AIRFLOW_METASTORE_DEFAULTS
            if hasattr(self.settings, "PHPMYADMIN_METASTORE_DEFAULTS"):
                self.services[f"{self.project_name}_phpmyadmin_metastore"] = self.settings.PHPMYADMIN_METASTORE_DEFAULTS
            elif hasattr(self.settings, "PGADMIN_METASTORE_DEFAULTS"):
                self.services[f"{self.project_name}_pgadmin_metastore"] = self.settings.PGADMIN_METASTORE_DEFAULTS
        elif hasattr(self.settings, "DAGSTER_METASTORE_DEFAULTS"):
            self.services[f"{self.project_name}_metastore"] = self.settings.DAGSTER_METASTORE_DEFAULTS
            if hasattr(self.settings, "PHPMYADMIN_METASTORE_DEFAULTS"):
                self.services[f"{self.project_name}_phpmyadmin_metastore"] = self.settings.PHPMYADMIN_METASTORE_DEFAULTS

        if hasattr(self.settings, "AIRFLOW_DEFAULTS"):
            self.services[f"{self.project_name}_orchestration"] = self.settings.AIRFLOW_DEFAULTS
            self.services[f"{self.project_name}_orchestration_webserver"] = self.settings.AIRFLOW_WEBSERVER
            self.services[f"{self.project_name}_orchestration_scheduler"] = self.settings.AIRFLOW_SCHEDULER
            self.services[f"{self.project_name}_orchestration_worker"] = self.settings.AIRFLOW_WORKER
            self.services[f"{self.project_name}_orchestration_triggerer"] = self.settings.AIRFLOW_TRIGGERER
            self.services[f"{self.project_name}_orchestration_redis"] = self.settings.REDIS_DEFAULTS
        elif hasattr(self.settings, "DAGSTER_WEBSERVER_DEFAULTS"):
            self.services[f"{self.project_name}_orchestration"] = self.settings.DAGSTER_WEBSERVER_DEFAULTS
            self.services[f"{self.project_name}_orchestration_daemon"] = self.settings.DAGSTER_DAEMON_DEFAULTS

        if hasattr(self.settings, "DBT_DEFAULTS"):
            self.services[f"{self.project_name}_data_modeling"] = self.settings.DBT_DEFAULTS
        elif hasattr(self.settings, "SQLMESH_DEFAULTS"):
            self.services[f"{self.project_name}_data_modeling"] = self.settings.SQLMESH_DEFAULTS
