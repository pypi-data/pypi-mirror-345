# src/managers/data_orchestration_manager.py

import click
import json
import os

from typing import Dict, List

from rapid_analytics_engineering.data_orchestration.airflow_orchestration import AirflowOrchestration
from rapid_analytics_engineering.data_orchestration.dagster_orchestration import DagsterOrchestration
from rapid_analytics_engineering.data_storage.postgresql_storage import PostgreSQLStorage
from rapid_analytics_engineering.data_storage.mysql_storage import MySQLStorage
from rapid_analytics_engineering.utility.base_manager import BaseManager
from rapid_analytics_engineering.utility.supported_tools import SUPPORTED_TOOLS


class DataOrchestrationManager(BaseManager):
    def __init__(self, project_name: str, network_name: str, config: Dict[str, str]):
        super().__init__(project_name, network_name, config)

    def init_orchestration_tool(self):
        orchestration_options: List[str] = list(SUPPORTED_TOOLS["data_orchestration"].keys())
        orchestration_option_nums: Dict[str, str] = {str(i + 1): name for i, name in enumerate(orchestration_options)}

        click.echo("Select your orchestration tool:")
        for num, name in orchestration_option_nums.items():
            click.echo(f"{num}: {name}")

        selected_number: str = click.prompt("Enter the number of your selection", type=click.Choice(orchestration_option_nums.keys()))
        selected_display: str = orchestration_option_nums[selected_number]
        selected_tool: str = SUPPORTED_TOOLS["data_orchestration"][selected_display]["tool_name"]

        default_orchestration_volume: str = f"{self.project_name}_data_orchestration"
        orchestration_volume: str = click.prompt(
            f"Enter volume name for {selected_tool} (or press Enter for default: {default_orchestration_volume})",
            default=default_orchestration_volume,
        )

        metastore_options_list: List[str] = SUPPORTED_TOOLS["data_orchestration"][selected_display]["metastore"]

        if len(metastore_options_list) > 1:
            metastore_choices = {str(i + 1): store for i, store in enumerate(metastore_options_list)}
            click.echo("Select your data orchestration metastore:")
            for num, store in metastore_choices.items():
                click.echo(f"{num}: {store}")
            selected_metastore_number: str = click.prompt("Enter number", type=click.Choice(metastore_choices.keys()))
            selected_metastore: str = metastore_choices[selected_metastore_number]
        else:
            selected_metastore: str = metastore_options_list[0]
            click.echo(f"{selected_tool} only supports {selected_metastore} as its metastore.")

        default_metastore_volume: str = f"{self.project_name}_{selected_tool}_metastore"
        metastore_volume: str = click.prompt(
            f"Enter volume name for {selected_metastore} metastore (or press Enter for default: {default_metastore_volume})",
            default=default_metastore_volume,
        )

        # 🧠 Check selected storage type to avoid duplicating setup
        selected_storage: str = self.config.get("data_storage")

        if selected_metastore != selected_storage:
            if selected_metastore == "postgresql":
                self.create_dir("postgres")
                self.generate_postgres_init(project_root=self.project_root)
            elif selected_metastore == "mysql":
                self.create_dir("mysql")
                self.generate_mysql_init(project_root=self.project_root)

        # 🔧 Orchestration script setup
        if selected_tool == "airflow":
            self.create_dir("airflow")
            self.generate_airflow_init(project_root=self.project_root)
        elif selected_tool == "dagster":
            self.create_dir("dagster")
            self.generate_dagster_init(project_root=self.project_root)

        self.config.update(
            {
                "data_orchestration": selected_tool,
                "orchestration_volume": orchestration_volume,
                "orchestration_metastore": selected_metastore,
                "metastore_volume": metastore_volume,
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

    def generate_airflow_init(self, project_root: str):
        airflow_helper: AirflowOrchestration = AirflowOrchestration(
            project_path=os.path.dirname(self.settings_path),
            storage_type=self.config.get("data_storage"),
            project_name=self.project_name,
        )
        airflow_helper.generate_airflow_init_file(output_path=os.path.join(project_root, "src/airflow", "airflow-init.sh"))

    def generate_dagster_init(self, project_root: str):
        dagster_helper: DagsterOrchestration = DagsterOrchestration(project_path=os.path.dirname(self.settings_path))
        dagster_helper.generate_dagster_yaml(output_path=os.path.join(project_root, "src/dagster", "dagster.yaml"))

    def generate_postgres_init(self, project_root: str):
        pg_metastore_helper: PostgreSQLStorage = PostgreSQLStorage(project_path=os.path.dirname(self.settings_path))
        pg_metastore_helper.generate_postgres_init(output_path=os.path.join(project_root, "src/postgres", "postgres-init.sh"))

    def generate_mysql_init(self, project_root: str):
        mysql_metastore_helper: MySQLStorage = MySQLStorage(project_path=os.path.dirname(self.settings_path))
        mysql_metastore_helper.generate_mysql_init(output_path=os.path.join(project_root, "src/mysql", "mysql-init.sh"))
