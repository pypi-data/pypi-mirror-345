import logging
import yaml

from typing import Dict

from rapid_analytics_engineering.utility.base_tool import BaseTool
from rapid_analytics_engineering.utility.indented_dumper import IndentedDumper


# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DockerComposeGenerator(BaseTool):
    """Generates the docker-compose.yml file using the user's settings.py."""

    def __init__(self, project_path: str):
        super().__init__(project_path)

    def generate_compose(self, output_path: str) -> None:
        """Generate a properly formatted docker-compose.yml file with correct spacing ONLY between services."""

        # Ensure each service has a network assigned
        for service_name, service_config in self.services.items():
            if "networks" not in service_config:
                service_config["networks"] = list(self.networks.keys())

        # Ensure lists (`ports`, `volumes`, `entrypoint`, `depends_on`) remain properly formatted
        for key in ["ports", "volumes", "entrypoint", "depends_on"]:
            for service in self.services.values():
                if key in service and isinstance(service[key], list):
                    service[key] = list(service[key])  # Ensure correct YAML list formatting

        # Extract volumes correctly from settings.py
        formatted_volumes: Dict = (
            {vol.strip(":"): {"name": vol.strip(":")} for vol in self.volumes.get("volumes", [])} if isinstance(self.volumes, dict) else {}
        )

        # Build the final Docker Compose configuration
        compose_config: Dict = {
            "services": self.services,
            "volumes": formatted_volumes if formatted_volumes else None,
            "networks": self.networks,
        }

        # Remove the `volumes` key if it's empty
        if not formatted_volumes:
            compose_config.pop("volumes", None)

        # Write YAML file section by section
        with open(output_path, "w") as f:
            f.write("services:\n")

            # Dump each service individually with proper indentation
            for i, (service_name, service_config) in enumerate(compose_config["services"].items()):
                if i > 0:
                    f.write("\n")  # Add a blank line before each new service

                f.write("  " + service_name + ":\n")  # Indent service name under services

                # Generate YAML for service config and manually indent it
                service_yaml = yaml.dump(
                    service_config,
                    Dumper=IndentedDumper,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=4,  # Ensure proper indentation for service values
                )

                # Indent all lines inside the service config to align correctly
                indented_service_yaml = "\n".join("    " + line for line in service_yaml.split("\n"))

                f.write(indented_service_yaml)  # Write properly indented service config

            f.write("\n")  # Extra line after services block

            if "volumes" in compose_config:
                yaml.dump(
                    {"volumes": compose_config["volumes"]},
                    f,
                    Dumper=IndentedDumper,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2,
                )
                f.write("\n")  # Extra line after volumes block

            yaml.dump(
                {"networks": compose_config["networks"]},
                f,
                Dumper=IndentedDumper,
                default_flow_style=False,
                sort_keys=False,
                indent=2,
            )

        logger.info(f"Docker Compose file generated at {output_path} with services: {list(self.services.keys())}")
