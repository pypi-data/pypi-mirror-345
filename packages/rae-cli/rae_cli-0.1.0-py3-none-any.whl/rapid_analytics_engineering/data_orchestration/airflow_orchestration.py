import logging

from textwrap import dedent

from rapid_analytics_engineering.utility.base_tool import BaseTool
from rapid_analytics_engineering.utility.shell_script_writer import ShellScriptWriter

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AirflowOrchestration(BaseTool):
    """
    This class handles necessary file generation for Airflow to run in Docker.
    It generates all shell scripts that create the Airflow container including:
        - Airflow Scheduler
        - Airflow Web Server
        - Airflow Worker
    """

    def __init__(self, project_path: str, storage_type: str, project_name: str) -> None:
        super().__init__(project_path)
        self.storage_type: str = storage_type
        self.storage_propername: str = "PostgreSQL" if self.storage_type == "postgresql" else "MySQL"
        self.storage_shortname: str = "postgres" if self.storage_type == "postgresql" else "mysql"
        self.project_name: str = project_name

    def generate_airflow_init_file(self, output_path: str) -> None:

        sh_init: str = dedent(
            f"""
            set -e

            echo "🔄 Waiting for Airflow DB to be ready..."

            until airflow db check >/dev/null 2>&1; do
                echo "⏳ Still waiting for metastore..."
                sleep 2
            done

            echo "✅ Airflow DB connection succeeded!"

            # Marker file for one-time DB initialization
            INIT_MARKER="/opt/airflow/.airflow-initialized"

            if [ ! -f "$INIT_MARKER" ]; then
                echo "🛠️ Running airflow db upgrade..."
                airflow db upgrade
                touch "$INIT_MARKER"
            else
                echo "🧠 Airflow DB already initialized. Skipping upgrade."
            fi

            # Only run user creation on first startup of webserver/standalone
            if [ "$ENV_MODE" = "dev" ] && [[ "$1" == "webserver" || "$1" == "standalone" ]]; then
                echo "👤 Checking for existing Airflow user..."
                EXISTING=$(airflow users list | grep -c admin || true)

                if [ "$EXISTING" -eq 0 ]; then
                    echo "👤 Creating default Airflow admin user..."
                    airflow users create \
                        --username admin \
                        --firstname Admin \
                        --lastname Admin \
                        --role Admin \
                        --email example@example.com \
                        --password securepassword
                else
                    echo "ℹ️ Admin user already exists."
                fi
            fi

            echo "🚀 Starting Airflow service: $@"

            exec airflow "$@"
        """
        )

        ShellScriptWriter.write_executable_script(output_path, sh_init)
