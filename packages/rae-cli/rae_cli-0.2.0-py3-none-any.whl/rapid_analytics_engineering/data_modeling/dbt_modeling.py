import logging
import shutil

from os import chmod, path, makedirs
from textwrap import dedent
from typing import List

from rapid_analytics_engineering.utility.base_tool import BaseTool
from rapid_analytics_engineering.utility.dockerfile_writer import DockerfileWriter
from rapid_analytics_engineering.utility.shell_script_writer import ShellScriptWriter

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class DbtModeling(BaseTool):
    """
    This class handles necessary file generation for dbt to run in Docker.
    It generates all shell scripts that create the dbt container and ensures the
    container only runs when called. ie this is a utility container not a full time running container.
    """

    def __init__(self, project_path: str, storage_type: str, project_name: str) -> None:
        super().__init__(project_path)
        self.storage_type: str = storage_type
        self.storage_propername: str = "PostgreSQL" if self.storage_type == "postgresql" else "MySQL"
        self.storage_shortname: str = "postgres" if self.storage_type == "postgresql" else "mysql"
        self.project_name: str = project_name

    def generate_dbt_dockerfile(self, output_path: str) -> None:
        dockerfile: str = dedent(
            f"""
            # Use latest slim Python image
            FROM python:3.12-slim

            # Set working directory
            WORKDIR /dbt

            # Install system-level dependencies
            RUN apt-get update && apt-get install -y \\
                build-essential \\
                git \\
                curl \\
                netcat-openbsd \\
                && apt-get clean \\
                && rm -rf /var/lib/apt/lists/*

            RUN pip install --no-cache-dir \\
                dbt-core \\
                dbt-{self.storage_shortname}
        """
        )

        # Write to file properly with correct spacing
        DockerfileWriter.write_dockerfile(output_path, dockerfile)

    def generate_dbt_docker_ignore(self, output_path: str) -> None:
        dockerignore: str = dedent(
            """
            # ignore dbt.sh - it should only exist on the host machine
            dbt.sh
        """
        )

        DockerfileWriter.write_dockerfile(output_path, dockerignore)

    def generate_dbt_init_file(self, output_path: str) -> None:
        """
        Generates the dbt container's entry script, which waits for the DB,
        verifies dbt is installed, and sets up the profiles.yml connection config.
        """
        content: str = dedent(
            f"""
            echo "🔄 Waiting for {self.storage_propername} to start..."
            while ! (echo > /dev/tcp/{self.project_name}_data_storage/${{DB_PORT}}) 2>/dev/null; do
                sleep 0.1
            done
            echo "✅ {self.storage_propername} is up!"

            cd /dbt || exit 1

            # Ensure dbt is installed
            if ! command -v dbt &> /dev/null; then
                echo "❌ dbt not found in container!"
                exit 1
            fi

            # Optional: Install git if missing (some dbt features depend on it)
            if ! command -v git &> /dev/null; then
                echo "📦 Installing git..."
                apt-get update && apt-get install -y git
            fi

            # Ensure dbt profiles directory exists
            mkdir -p /root/.dbt

            # Always overwrite profiles.yml to ensure clean connection
            cat > /root/.dbt/profiles.yml <<EOL
            {self.project_name}_data_modeling:
              target: dev
              outputs:
                dev:
                  type: {self.storage_shortname}
                  host: {self.project_name}_data_storage
                  user: admin
                  password: securepassword
                  port: ${{DB_PORT}}
                  dbname: {self.project_name}_db
                  schema: public
                  threads: 4
            EOL

            echo "✅ profiles.yml configured for {self.storage_type} container"

            # Leave container running for debugging
            exec tail -f /dev/null
        """
        )

        ShellScriptWriter.write_executable_script(output_path, content)

    def generate_dbt_wrapper(self, output_path: str, project_name: str) -> None:
        """
        Generates a wrapper script that lets the user run `dbt` commands directly
        as if they were on their machine (e.g., `dbt run`), by exec'ing into the container.

        This wrapper abstracts away container details so the user can just use `dbt` normally.
        """
        container_name: str = f"{project_name}_data_modeling"
        user_bin_path: str = path.expanduser("~/.local/bin")
        destination_path: str = path.join(user_bin_path, "dbt")

        wrapper_script: str = dedent(
            f"""
            echo "🔥 dbt wrapper in use..."
            echo "This allows you to interact with the dbt Docker container via dbt commands"

            if ! docker ps --format '{{{{.Names}}}}' | grep -q '^{container_name}$'; then
                echo "❌ Container '{container_name}' is not running."
                echo "💡 Run: docker-compose up -d {container_name}"
                exit 1
            fi

            docker exec -it {container_name} dbt "$@"
        """
        )

        # Write the script locally first
        ShellScriptWriter.write_executable_script(output_path, wrapper_script)

        # Ensure the local bin directory exists
        makedirs(user_bin_path, exist_ok=True)
        # Move dbt wrapper to users local/bin directory & ensure it can be executed
        try:
            shutil.copy2(output_path, destination_path)
            chmod(destination_path, 0o755)
            logger.info(f"✅ dbt wrapper script installed as 'dbt' in {user_bin_path}.")
        except PermissionError:
            logger.warning("❌ Failed to install dbt wrapper script due to permission issues.")
            logger.warning("Please manually move the script to a directory in your PATH, e.g.:")
            logger.warning(f"\tsudo mv {output_path} /usr/local/bin/dbt")
            return

        logger.info("⚡ You can now use the `dbt` command directly, e.g.: `dbt run`, `dbt build`")

    def generate_dbt_project(self, output_path: str) -> None:
        """
        Generates the required folders and dbt_project.yml in {project_name}/src/dbt
        """
        dbt_project_path: str = path.join(output_path, "dbt_project.yml")
        directories: List[str] = ["analyses", "macros", "models", "seeds", "snapshots", "tests"]

        for dir_name in directories:
            dir_to_create: str = path.join(output_path, dir_name)
            makedirs(dir_to_create, exist_ok=True)

        # Write dbt_project.yml
        dbt_project: str = dedent(
            f"""
            name: '{self.project_name}'
            version: '1.0.0'

            profile: '{self.project_name}_data_modeling'

            model-paths: ["models"]
            analysis-paths: ["analyses"]
            test-paths: ["tests"]
            seed-paths: ["seeds"]
            macro-paths: ["macros"]
            snapshot-paths: ["snapshots"]

            clean-targets:
              - "target"
              - "dbt_packages"

            models:
              {self.project_name}:
                example:
                  +materialized: view
        """
        )

        DockerfileWriter.write_dockerfile(dbt_project_path, dbt_project)

        logger.info(f"✅ dbt project scaffolded at {output_path}")
