import click
import json
import os

from textwrap import dedent
from typing import Dict, List

from rapid_analytics_engineering.data_modeling.dbt_modeling import DbtModeling
from rapid_analytics_engineering.data_modeling.sql_mesh_modeling import SQLMeshModeling
from rapid_analytics_engineering.utility.base_manager import BaseManager
from rapid_analytics_engineering.utility.supported_tools import SUPPORTED_TOOLS


class DataModelingManager(BaseManager):
    def __init__(self, project_name: str, network_name: str, config: Dict[str, str]):
        super().__init__(project_name, network_name, config)

    def init_data_modeling_tool(self):
        # Extract display names for choices
        modeling_options: List[str] = list(SUPPORTED_TOOLS["data_modeling"].keys())

        # Create a numbered list for display
        modeling_option_nums: Dict = {str(i + 1): name for i, name in enumerate(modeling_options)}

        # Display formatted choices
        click.echo("Select your data modeling tool:")
        for num, name in modeling_option_nums.items():
            click.echo(f"{num}: {name}")

        selected_model_number: str = click.prompt("Enter the number of your selection", type=click.Choice(modeling_option_nums.keys()))
        selected_modeling_display: str = modeling_option_nums[selected_model_number]
        selected_data_modeling: str = SUPPORTED_TOOLS["data_modeling"][selected_modeling_display]
        default_data_modeling_volume: str = f"{self.project_name}_data_modeling"
        selected_storage: str = self.config.get("data_storage")
        data_modeling_volume: str = click.prompt(
            dedent(f"Enter volume name for {selected_data_modeling} (or press Enter for default: {default_data_modeling_volume})"),
            default=default_data_modeling_volume,
        )

        if selected_data_modeling == "dbt":
            self.create_dir(tool_name="dbt")
            self.generate_dbt_dockerfiles(
                project_root=os.path.abspath(self.project_name),
                storage_type=selected_storage,
                project_name=self.project_name,
            )
        elif selected_data_modeling == "sqlmesh":
            self.create_dir(tool_name="sqlmesh")
            self.generate_sql_mesh_dockerfiles(
                project_root=os.path.abspath(self.project_name),
                storage_type=selected_storage,
                project_name=self.project_name,
            )

        self.config.update(
            {
                "data_modeling": selected_data_modeling,
                "data_modeling_volume": data_modeling_volume,
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

    def generate_dbt_dockerfiles(self, project_root: str, storage_type: str, project_name: str) -> None:
        dbt_generator: DbtModeling = DbtModeling(
            project_path=os.path.dirname(self.settings_path),
            storage_type=storage_type,
            project_name=project_name,
        )

        dbt_generator.generate_dbt_dockerfile(
            output_path=os.path.join(project_root, "src/dbt", "Dockerfile"),
        )

        dbt_generator.generate_dbt_docker_ignore(
            output_path=os.path.join(project_root, "src/dbt", ".dockerignore"),
        )

        dbt_generator.generate_dbt_init_file(
            output_path=os.path.join(project_root, "src/dbt", "dbt-init.sh"),
        )

        dbt_generator.generate_dbt_wrapper(
            output_path=os.path.join(project_root, "src/dbt", "dbt.sh"),
            project_name=project_name,
        )

        dbt_generator.generate_dbt_project(
            output_path=os.path.join(project_root, "src/dbt"),
        )

    def generate_sql_mesh_dockerfiles(self, project_root: str, storage_type: str, project_name: str) -> None:
        sql_mesh_generator: SQLMeshModeling = SQLMeshModeling(
            project_path=os.path.dirname(self.settings_path),
            storage_type=storage_type,
            project_name=project_name,
        )

        sql_mesh_generator.generate_sql_mesh_dockerfile(
            output_path=os.path.join(project_root, "src/sql_mesh", "Dockerfile"),
        )

        sql_mesh_generator.generate_sql_mesh_init_file(
            output_path=os.path.join(project_root, "src/sql_mesh", "sqlmesh-init.sh"),
        )

        sql_mesh_generator.generate_sql_mesh_wrapper(
            output_path=os.path.join(project_root, "src/sql_mesh", "sqlmesh.sh"),
        )
