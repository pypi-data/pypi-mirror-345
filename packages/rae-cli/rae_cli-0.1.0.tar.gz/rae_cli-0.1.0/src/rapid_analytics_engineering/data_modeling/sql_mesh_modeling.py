import logging
import shutil

from os import makedirs, path
from textwrap import dedent

from rapid_analytics_engineering.utility.base_tool import BaseTool
from rapid_analytics_engineering.utility.dockerfile_writer import DockerfileWriter
from rapid_analytics_engineering.utility.shell_script_writer import ShellScriptWriter

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SQLMeshModeling(BaseTool):
    """
    This class handles necessary file generation for SQL Mesh to run in Docker.
    It generates all shell scripts that create the SQL Mesh container requires and ensures the
    container only runs when called. ie this is a utility container not a full time running container.
    """

    def __init__(self, project_name: str, project_path: str, storage_type: str) -> None:
        super().__init__(project_path)
        self.project_name: str = project_name
        self.storage_type: str = storage_type
        self.storage_propername: str = "PostgreSQL" if self.storage_type == "postgresql" else "MySQL"
        self.storage_shortname: str = "postgres" if self.storage_type == "postgresql" else "mysql"

    def generate_sql_mesh_dockerfile(self, output_path: str) -> None:
        dockerfile: str = dedent(
            f"""
            # Use the latest stable Python 3 image as the base
            FROM python:3.12-slim

            # Set the working directory in the container
            WORKDIR /sql_mesh

            # Install netcat (openbsd version) and remove unnecessary files to keep image size small
            RUN apt-get update
            RUN apt-get install -y netcat-openbsd curl

            # Upgrade pip and install SQL Mesh for {self.storage_propername}
            RUN pip install --no-cache-dir --upgrade pip
            RUN pip install --no-cache-dir "psycopg2-binary"
            RUN pip install --no-cache-dir "sqlmesh[slack,github,web]"

            # Copy everything from the sql_mesh directory to /sql_mesh in the container
            COPY . /sql_mesh

            # Use sql_mesh-init.sh as the entrypoint
            ENTRYPOINT ["sqlmesh"]
            """
        )

        # Write to file properly with correct spacing
        DockerfileWriter.write_dockerfile(output_path, dockerfile)

    def generate_sql_mesh_init_file(self, output_path: str) -> None:
        """
        Generates the required sql_mesh init file with the correct bash syntax and env substitution.
        """
        content: str = dedent(
            f"""
            echo "🔄 Waiting for {self.storage_propername} to start..."

            while ! (echo > /dev/tcp/{self.project_name}_data_storage/${{DB_PORT}}) 2>/dev/null; do
                sleep 0.1

            done

            echo "✅ {self.storage_propername} is up!"

            cd /sql_mesh || exit 1

            # Ensure sqlmesh is installed
            if ! command -v sqlmesh &> /dev/null; then
                echo "❌ sqlmesh not found in container!"
                exit 1
            fi

            # Optional: Install git if missing (some SQLMesh features depend on it)
            if ! command -v git &> /dev/null; then
                echo "📦 Installing git..."
                apt-get update && apt-get install -y git
            fi

            PROJECT_NAME="${{PROJECT_NAME:-rae}}"
            PROJECT_DIR="/sql_mesh/{self.project_name}_data_modeling"
            CONFIG_FILE="$PROJECT_DIR/config.yaml"

            # Initialize SQLMesh project if needed
            if [ ! -d "$PROJECT_DIR" ]; then
                echo "🚧 Creating and initializing SQLMesh project..."
                mkdir -p "$PROJECT_DIR"
                cd "$PROJECT_DIR"
                sqlmesh init {self.storage_shortname}
                echo "✅ Project initialized."
            else
                echo "✅ SQLMesh project already exists, skipping init."
            fi

            # Overwrite config.yaml with real values (even if init created a stub)
            echo "🛠 Writing production-ready config.yaml..."
            cat > "$CONFIG_FILE" <<EOL
            config:
                default_catalog: main
                default_schema: public
                gateway:
                    type: {self.storage_type}
                    host: {self.project_name}_data_storage
                    user: admin
                    password: securepassword
                    port: ${{DB_PORT}}
                    database: {self.project_name}_db

            model_defaults:
                dialect: {self.storage_shortname}
            EOL

            echo "✅ config.yaml created and configured."

            echo "🚀 SQLMesh container initialized and ready!"
            exec tail -f /dev/null
        """
        )

        ShellScriptWriter.write_executable_script(output_path, content)

    def generate_sql_mesh_wrapper(self, output_path: str) -> None:
        """
        Generates a wrapper script that lets the user run `sqlmesh` commands directly
        as if they were on their machine (e.g., `sqlmesh plan`, `sqlmesh run`), by exec'ing into the container.
        """

        container_name: str = f"{self.project_name}_data_modeling"
        user_bin_path: str = path.expanduser("~/.local/bin")
        destination_path: str = path.join(user_bin_path, "sqlmesh")

        wrapper_script: str = dedent(
            f"""
            docker exec -it {container_name} sqlmesh "$@"
        """
        )

        ShellScriptWriter.write_executable_script(output_path, wrapper_script)

        # Ensure local bin directory exists
        makedirs(user_bin_path, exist_ok=True)

        try:
            shutil.copy(output_path, destination_path)
            logger.info(f"✅ sqlmesh wrapper script installed as 'sqlmesh' in {user_bin_path}.")
        except PermissionError:
            logger.warning("❌ Failed to install sqlmesh wrapper script due to permission issues.")
            logger.warning(f"Please manually move the script to a directory in your PATH, e.g.:")
            logger.warning(f"\tsudo mv {output_path} /usr/local/bin/sqlmesh")
            return

        logger.info("⚡ You can now use the `sqlmesh` command directly, e.g.: `sqlmesh plan`, `sqlmesh run`")
