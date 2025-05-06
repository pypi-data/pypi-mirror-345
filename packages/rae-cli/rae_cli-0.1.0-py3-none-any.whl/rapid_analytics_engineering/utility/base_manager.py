import logging
import os

from typing import Dict

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class BaseManager:
    """
    Base class for the tool level manager classes that feed into the CLI's prompt logic.
    This is where all shared manager level logic can be encapsulated then inherited by downstream classes.
    """

    def __init__(self, project_name: str, network_name: str, config: Dict[str, str]):
        self.project_name: str = project_name
        self.network_name: str = network_name or f"{self.project_name}_network"
        self.config: Dict[str, str] = config

        self.project_root: str = os.path.abspath(self.project_name)
        self.settings_path: str = os.path.join(self.project_root, "src/settings/settings.py")
        self.config_path: str = os.path.join(self.project_root, "src/settings/project_config.json")

    def get_project_root(self) -> str:
        return self.project_root

    def get_settings_path(self) -> str:
        return self.settings_path

    def get_config_path(self) -> str:
        return self.config_path

    def create_dir(self, tool_name: str) -> None:
        os.makedirs(f"{self.project_name}/src/{tool_name}", exist_ok=True)
