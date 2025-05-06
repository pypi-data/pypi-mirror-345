from textwrap import dedent

from rapid_analytics_engineering.utility.base_tool import BaseTool
from rapid_analytics_engineering.utility.shell_script_writer import ShellScriptWriter


class MySQLStorage(BaseTool):
    """
    This class handles necessary file generation for MySQL to run in Docker.
    It generates all shell scripts that create the databases and users needed for the project.
    """

    def __init__(self, project_path: str) -> None:
        super().__init__(project_path)

    def generate_mysql_init(self, output_path: str) -> None:
        """
        Generates all shell scripts that create the databases and users needed for the project.
        """

        content: str = dedent(
            """
        set -e

        echo "🔧 Initializing MySQL databases and users..."

        IFS=',' read -ra DBS <<< "$MYSQL_MULTIPLE_DATABASES"

        for db in "${DBS[@]}"; do
            echo "📦 Creating database '$db'..."
            mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS \`${db}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        done

        echo "👤 Creating 'admin' user..."
        mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE USER IF NOT EXISTS 'admin'@'%' IDENTIFIED BY 'securepassword';"

        for db in "${DBS[@]}"; do
            echo "🔐 Granting privileges to 'admin' on '$db'..."
            mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "GRANT ALL PRIVILEGES ON \`${db}\`.* TO 'admin'@'%';"
        done

        mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;"

        echo "🎉 MySQL initialization complete!"
        """
        )

        ShellScriptWriter.write_executable_script(output_path, dedent(content))
