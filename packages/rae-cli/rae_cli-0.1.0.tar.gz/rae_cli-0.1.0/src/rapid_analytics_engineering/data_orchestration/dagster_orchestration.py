import logging

from textwrap import dedent

from rapid_analytics_engineering.utility.base_tool import BaseTool
from rapid_analytics_engineering.utility.dockerfile_writer import DockerfileWriter

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DagsterOrchestration(BaseTool):
    """
    This class handles necessary file generation for Dagster to run in Docker.
    It generates all shell scripts that create the Dagster container.
    """

    def __init__(self, project_path: str, storage_type: str, project_name: str) -> None:
        super().__init__(project_path)
        self.storage_type: str = storage_type
        self.storage_propername: str = "PostgreSQL" if self.storage_type == "postgresql" else "MySQL"
        self.storage_shortname: str = "postgres" if self.storage_type == "postgresql" else "mysql"
        self.project_name: str = project_name
        self.host_name: str = ""

        # Determine hostname based on storage selection
        if self.storage_type == "postgresql":
            self.host_name = f"{self.project_name}_data_storage"
        else:
            self.host_name = f"{self.project_name}_metastore"

    def generate_dagster_dockerfile(self, output_path: str) -> None:
        """Generate the required Dockerfile for Dagster"""

        dockerfile: str = dedent(
            f"""
            FROM python:3.12-slim

            # Set working directory
            WORKDIR /opt/dagster/app

            # Install system-level dependencies
            RUN apt-get update && \\
                apt-get install -y build-essential curl libpq-dev git && \\
                rm -rf /var/lib/apt/lists/*

            # Install Dagster and Postgres adapter
            RUN pip install --no-cache-dir \\
                dagster \\
                dagster-graphql \\
                dagster-webserver \\
                dagster-postgres \\
                dagster-docker \\
                dagit

            # Set Dagster home (required for config resolution)
            ENV DAGSTER_HOME=/opt/dagster/app
        """
        )

        # Write to file properly with correct spacing
        DockerfileWriter.write_dockerfile(output_path, dockerfile)

    def generate_dagster_config_yaml(self, output_path: str) -> None:
        """Generate dagster.yaml, workspace.yaml, and repo.py for DAGSTER_HOME"""

        # === dagster.yaml ===
        dagster_yaml: str = dedent(
            f"""
            local_artifact_storage:
              module: dagster.core.storage.root
              class: LocalArtifactStorage
              config:
                base_dir: /opt/dagster/app/storage

            compute_logs:
              module: dagster.core.storage.local_compute_log_manager
              class: LocalComputeLogManager
              config:
                base_dir: /opt/dagster/app/storage/logs

            run_storage:
              module: dagster_postgres.run_storage
              class: PostgresRunStorage
              config:
                postgres_db:
                  username: admin
                  password: securepassword
                  hostname: {self.host_name}
                  db_name: {self.project_name}_metastore

            event_log_storage:
              module: dagster_postgres.event_log
              class: PostgresEventLogStorage
              config:
                postgres_db:
                  username: admin
                  password: securepassword
                  hostname: {self.host_name}
                  db_name: {self.project_name}_metastore

            schedule_storage:
              module: dagster_postgres.schedule_storage
              class: PostgresScheduleStorage
              config:
                postgres_db:
                  username: admin
                  password: securepassword
                  hostname: {self.host_name}
                  db_name: {self.project_name}_metastore

            run_coordinator:
              module: dagster.core.run_coordinator
              class: QueuedRunCoordinator

            run_launcher:
              module: dagster.core.launcher
              class: DefaultRunLauncher
        """
        )

        DockerfileWriter.write_dockerfile(output_path, dagster_yaml)

    def generate_dagster_workspace_yaml(self, output_path: str) -> None:

        # === workspace.yaml ===
        workspace_yaml: str = dedent(
            """
            load_from:
              - python_file:
                  relative_path: repo.py
                  attribute: define_assets
        """
        )

        DockerfileWriter.write_dockerfile(output_path, workspace_yaml)

    def generate_dagster_repo(self, output_path: str) -> None:
        # === repo.py ===
        repo_py: str = dedent(
            """
            from dagster import job, op, Definitions

            @op
            def hello_op():
                print("👋 Hello from Dagster!")

            @job
            def hello_job():
                hello_op()

            def define_assets():
                return Definitions(jobs=[hello_job])
        """
        )

        DockerfileWriter.write_dockerfile(output_path, repo_py)
