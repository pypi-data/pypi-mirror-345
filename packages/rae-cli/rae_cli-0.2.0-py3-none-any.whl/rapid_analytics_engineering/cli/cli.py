import click
import json
import os
import logging
import sys

from typing import Dict

from rapid_analytics_engineering.easter_eggs.wildflower import WildFlower
from rapid_analytics_engineering.generators.docker_compose_generator import DockerComposeGenerator
from rapid_analytics_engineering.managers.data_modeling_manager import DataModelingManager
from rapid_analytics_engineering.managers.data_orchestration_manager import DataOrchestrationManager
from rapid_analytics_engineering.managers.data_storage_manager import DataStorageManager
from rapid_analytics_engineering.managers.settings_manager import SettingsManager
from rapid_analytics_engineering.utility.supported_tools import SUPPORTED_TOOLS

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RaeCLI:
    """CLI class for RAE (Rapid Analytics Engineering)."""

    def __init__(self):
        self.config: Dict[str, str] = {}
        self.project_name: str = ""
        self.network_name: str = ""
        self.config_path: str = ""
        self.settings_path: str = os.path.abspath(os.path.join(os.getcwd(), self.project_name, "src/settings/settings.py"))

    def create_settings_dir(self) -> None:
        os.makedirs(f"{self.project_name}/src/settings", exist_ok=True)

    def set_settings_path(self) -> None:
        """Ensure we always set the correct absolute path to settings.py inside the user's project."""
        self.settings_path = os.path.abspath(os.path.join(os.getcwd(), self.project_name, "src/settings/settings.py"))

    def set_config_path(self) -> None:
        self.config_path = f"{self.project_name}/src/settings/project_config.json"

    def init_project(self):
        """Initialize the project structure and store user selections."""
        click.echo("Starting project initialization")

        self.project_name = click.prompt("Enter your project name")
        self.network_name = f"{self.project_name}_network"
        project_path: str = os.path.join(os.getcwd(), self.project_name)
        settings_path: str = os.path.join(self.project_name, "src", "settings", "settings.py")

        if os.path.exists(project_path):
            print(f"Project '{self.project_name}' already exists at {project_path}.")
            print("Initialization aborted to prevent overwriting your existing project.")
            print(f"Please delete the existing project ({self.project_name}) or choose a different project name.")
            sys.exit(1)  # Immediately terminate the program

        self.create_settings_dir()
        self.set_settings_path()
        self.set_config_path()

        # DATA STORAGE
        data_storage_manager: DataStorageManager = DataStorageManager(self.project_name, self.network_name, self.config)
        data_storage_manager.init_data_storage_tool()

        # DATA MODELING
        data_modeling_manager: DataModelingManager = DataModelingManager(self.project_name, self.network_name, self.config)
        data_modeling_manager.init_data_modeling_tool()

        # DATA ORCHESTRATION LOGIC
        data_orchestration_manager: DataOrchestrationManager = DataOrchestrationManager(self.project_name, self.network_name, self.config)
        data_orchestration_manager.init_orchestration_tool()

        logger.info(f"User selections saved to {self.config_path}")

        # Ensure the directory exists
        os.makedirs(os.path.dirname(settings_path), exist_ok=True)

        # Generate settings file in the correct directory
        SettingsManager.generate_settings_file(
            data_modeling_volume=self.config["data_modeling_volume"],
            metastore_volume=self.config["metastore_volume"],
            orchestration_volume=self.config["orchestration_volume"],
            network_name=self.config["network_name"],
            output_path=settings_path,
            project_name=self.config["project_name"],
            storage_volume=self.config["storage_volume"],
            config=self.config,
        )

        click.echo(f"🎉 Project '{self.project_name}' initialized successfully!")
        click.echo(f"🔧 Project configuration file created at: {self.config_path}")
        click.echo(f"🔧 Settings file created at: {self.settings_path}")

    def display_summary(self):
        """Display the summary of the user selections."""
        click.echo("\nConfiguration Summary:")
        click.echo(f"- Project Name: {self.config['project_name']}")
        click.echo(f"- Network Name: {self.config['network_name']}")
        click.echo(f"- Data Storage: {self.config['data_storage']}")
        click.echo(f"- Data Modeling: {self.config['data_modeling']}")
        click.echo(f"- Data Orchestration: {self.config['data_orchestration']}")
        click.echo(f"- Data Orchestration Metastore: {self.config['orchestration_metastore']}")
        click.echo()

    def generate_docker_compose(self, project_name: str = None) -> None:
        """Generate the Docker Compose and tool configuration files."""
        logger.info("Starting docker-compose file generation")

        # If project_name is not provided, default to self.project_name
        if project_name:
            self.project_name = project_name

        # Locate the user's project root dynamically
        project_root: str = os.path.abspath(self.project_name)

        # Ensure we set the correct absolute path for settings.py
        self.settings_path: str = os.path.join(project_root, "src/settings/settings.py")

        # Ensure settings.py exists
        if not os.path.exists(self.settings_path):
            click.echo(f"Error: settings.py not found at {self.settings_path}. Run `rae init` first.")
            raise FileNotFoundError("settings.py is missing. Have you initialized the project?")

        # Initialize DockerComposeGenerator using the detected project root
        compose_generator: DockerComposeGenerator = DockerComposeGenerator(project_path=os.path.dirname(self.settings_path))

        # Generate the Docker Compose file
        compose_generator.generate_compose(output_path=os.path.join(project_root, "src", "docker-compose.yml"))

        click.echo(f"Docker Compose file has been generated at {os.path.join(project_root, 'src', 'docker-compose.yml')}")

    def list_services(self):
        """List all configured services."""
        if not os.path.exists(self.config_path):
            click.echo("Error: Configuration file not found. Run `rae init` first.")
            return

        with open(self.config_path, "r") as f:
            config = json.load(f)

        click.echo("Configured Services:")
        click.echo(f"- Data Storage Tool: {config.get('data_storage', 'Not configured')}")
        click.echo(f"- Modeling Tool: {config.get('data_modeling', 'Not configured')}")
        click.echo(f"- Orchestration Tool: {config.get('data_orchestration', 'Not configured')}")

    def reset_config(self, force):
        """
        Reset the project configuration.

        Args:
            force (bool): If True, skip confirmation and reset immediately.
            passed via the CLI using --force
        """
        if not force:
            confirm: bool = click.confirm("Are you sure you want to reset the configuration?", default=False)
            if not confirm:
                click.echo("Operation canceled.")
                return

        # Remove files if they exists
        for file_path in [self.config_path, self.settings_path]:
            if os.path.exists(file_path):
                os.remove(file_path)
                click.echo(f"Removed {file_path}")
            else:
                click.echo(f"File not found: {file_path}")

        click.echo("Configuration reset complete.")

    def draw_wildflower(self):
        flower: WildFlower = WildFlower()

        flower.draw_wildflower()
