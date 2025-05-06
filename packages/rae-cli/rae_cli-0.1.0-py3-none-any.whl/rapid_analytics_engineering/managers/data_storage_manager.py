import click
import json
import os

from typing import Dict, List

from rapid_analytics_engineering.data_storage.mysql_storage import MySQLStorage
from rapid_analytics_engineering.data_storage.postgresql_storage import PostgreSQLStorage
from rapid_analytics_engineering.utility.base_manager import BaseManager
from rapid_analytics_engineering.utility.supported_tools import SUPPORTED_TOOLS


class DataStorageManager(BaseManager):
    def __init__(self, project_name: str, network_name: str, config: Dict[str, str]):
        super().__init__(project_name, network_name, config)

    def init_data_storage_tool(self):
        storage_options: List[str] = list(SUPPORTED_TOOLS["data_storage"].keys())
        storage_option_nums: Dict[str, str] = {str(i + 1): name for i, name in enumerate(storage_options)}

        click.echo("Select your data storage tool:")
        for num, name in storage_option_nums.items():
            click.echo(f"{num}: {name}")

        selected_storage_number: str = click.prompt("Enter the number of your selection", type=click.Choice(storage_option_nums.keys()))
        selected_storage_display: str = storage_option_nums[selected_storage_number]
        selected_storage: str = SUPPORTED_TOOLS["data_storage"][selected_storage_display]

        default_storage_volume: str = f"{self.project_name}_data_storage"
        data_storage_volume: str = click.prompt(
            f"Enter volume name for {selected_storage} (or press Enter for default: {default_storage_volume})",
            default=default_storage_volume,
        )

        if selected_storage == "postgresql":
            self.create_dir(tool_name="postgres")
            self.generate_postgres_init(project_root=os.path.abspath(self.project_name))
        elif selected_storage == "mysql":
            self.create_dir(tool_name="mysql")
            self.generate_mysql_init(project_root=os.path.abspath(self.project_name))

        self.config.update(
            {
                "data_storage": selected_storage,
                "network_name": self.network_name,
                "project_name": self.project_name,
                "storage_volume": data_storage_volume,
            }
        )

        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                existing_config = json.load(f)
        else:
            existing_config = {}

        existing_config.update(self.config)

        with open(self.config_path, "w") as f:
            json.dump(existing_config, f, indent=4)

    def generate_postgres_init(self, project_root: str):
        pg_helper: PostgreSQLStorage = PostgreSQLStorage(project_path=os.path.dirname(self.settings_path))

        pg_helper.generate_postgres_init(output_path=os.path.join(project_root, "src/postgres", "postgres-init.sh"))

    def generate_mysql_init(self, project_root: str):
        mysql_helper: MySQLStorage = MySQLStorage(project_path=os.path.dirname(self.settings_path))

        mysql_helper.generate_mysql_init(output_path=os.path.join(project_root, "src/mysql", "mysql-init.sh"))
