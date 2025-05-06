from textwrap import dedent

from rapid_analytics_engineering.utility.base_tool import BaseTool
from rapid_analytics_engineering.utility.shell_script_writer import ShellScriptWriter


class PostgreSQLStorage(BaseTool):
    """
    This class handles necessary file generation for PostgreSQL to run in Docker.
    It generates a shell script that creates the databases and users needed for the project.
    """

    def __init__(self, project_path: str) -> None:
        super().__init__(project_path)

    def generate_postgres_init(self, output_path: str) -> None:
        postgres_init: str = dedent(
            """
            set -e

            echo "🔧 Configuring PostgreSQL for local development..."
            echo "📄 POSTGRES_MULTIPLE_DATABASES: $POSTGRES_MULTIPLE_DATABASES"
            echo "📄 POSTGRES_USER: $POSTGRES_USER"

            # Wait until PostgreSQL is ready to accept connections
            echo "⏳ Waiting for PostgreSQL to start..."

            until pg_isready -U "$POSTGRES_USER" -d postgres; do
                sleep 2
            done

            echo "✅ PostgreSQL is ready!"

            DBS="$POSTGRES_MULTIPLE_DATABASES"

            if [ -z "$DBS" ]; then
                echo "❌ No databases specified in POSTGRES_MULTIPLE_DATABASES. Exiting."
                exit 1
            fi

            IFS=',' read -ra DBS <<< "$DBS"

            for db in "${DBS[@]}"; do
                echo "🔍 Checking existence of '$db'..."
                psql -U "$POSTGRES_USER" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname='${db}';" || echo "⚠️ Failed SELECT on $db"

                echo "📦 Creating database '$db' if it doesn't already exist..."
                if ! psql -U "$POSTGRES_USER" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname='${db}';" | grep -q 1; then
                    echo "🚧 Creating $db..."
                    psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE ${db} OWNER $POSTGRES_USER;" || echo "❌ Failed to create $db"
                else
                    echo "✅ '$db' already exists. Skipping creation."
                fi

                echo "🔐 Granting privileges on $db to $POSTGRES_USER..."
                psql -U "$POSTGRES_USER" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${db} TO $POSTGRES_USER;" || \\
                    echo "❌ Failed to grant privileges on $db"
            done

            echo "🎉 PostgreSQL initialization complete!"
        """
        )

        ShellScriptWriter.write_executable_script(output_path, postgres_init)
