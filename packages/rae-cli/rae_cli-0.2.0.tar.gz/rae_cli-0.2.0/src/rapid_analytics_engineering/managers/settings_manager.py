from textwrap import dedent
from typing import Dict, List


class SettingsManager:
    """Handles the creation and management of the user's settings.py file."""

    @staticmethod
    def generate_settings_file(
        data_modeling_volume: str,
        metastore_volume: str,
        network_name: str,
        output_path: str,
        orchestration_volume: str,
        project_name: str,
        config: Dict,
        storage_volume: str,
    ):
        """
        Generates the user's settings.py file using their selected inputs for:
            - Data Storage
                - with necessary volume for local-dev data persisitence
            - Data Modeling
                - implemented as a utility container
            - Orchestration
                - with separate metastore db instance from the data storage layer
        """

        summary: str = dedent(
            """
            '''
                This file allows you to customize each specific tool's configuration.
                Securely pass:
                    - container names
                    - port numbers
                    - environment configuration values for tools including user_name, passwords, etc
                    - network configurations for inter-service communication between containers
            '''
        """
        )

        network: str = f"""
            # Network Configuration
            NETWORKS = {{
                "{network_name}": {{
                    "name": "{network_name}",
                    "driver": "bridge",
                }}
            }}
        """

        output_project_name: str = f"""
            # Project Name
            PROJECT_NAME = "{project_name}"
        """

        data_orchestration_tool: str = "airflow" if "airflow" in config["data_orchestration"] else "dagster"
        data_storage_host: str = f"{project_name}_data_storage"
        data_storage_type: str = "postgres" if "postgresql" in config["data_storage"] else "mysql"
        data_storage_port: str = "5432" if "postgresql" in config["data_storage"] else "3306"
        metastore_port: str = "5432" if "postgresql" in config["orchestration_metastore"] else "3306"
        metastore_type: str = "postgres" if "postgresql" in config["orchestration_metastore"] else "mysql"
        use_combined_metastore: bool = data_storage_type == metastore_type
        settings: List[str] = []

        volumes: str = f"""
            # Volume Configuration
            VOLUMES = {{
                "volumes": [
                    "{storage_volume}:",
                    "{orchestration_volume}:",
                    "{metastore_volume}:",
                    "{data_modeling_volume}:",
                ]
            }}
        """

        settings.append("\n# Data Storage Configuration")

        # PostgreSQL Configuration (Production-Ready)
        if "postgresql" in config["data_storage"]:
            if use_combined_metastore and metastore_type == "postgres":
                dbs: List[str] = [f"{project_name}_db", f"{project_name}_metastore", "postgres"]
            else:
                dbs: List[str] = [f"{project_name}_db", "postgres"]

            dbs: str = ",".join(dbs)

            settings.append(
                f"""
                POSTGRES_DEFAULTS = {{
                    "container_name": "{data_storage_host}",
                    "image": "{data_storage_type}",
                    "restart": "always",
                    "ports": ["5432:5432"],
                    "environment": {{
                        "POSTGRES_USER": "admin",
                        "POSTGRES_PASSWORD": "securepassword",
                        "POSTGRES_DB": "postgres",
                        "POSTGRES_MULTIPLE_DATABASES": "{dbs}",
                    }},
                    "volumes": [
                        "{storage_volume}:/var/lib/postgresql/data",
                        "./postgres/postgres-init.sh:/docker-entrypoint-initdb.d/postgres-init.sh",
                    ],
                    "networks": ["{network_name}"],
                    "healthcheck": {{
                        "test": ["CMD-SHELL", "pg_isready -U admin -d postgres"],
                        "interval": "10s",
                        "timeout": "5s",
                        "retries": 5,
                    }},
                }}

                PGADMIN_DEFAULTS = {{
                    "container_name": "{project_name}_pgadmin",
                    "image": "dpage/pgadmin4",
                    "restart": "always",
                    "ports": ["5050:80"],
                    "environment": {{
                        "PGADMIN_DEFAULT_EMAIL": "admin@admin.com",
                        "PGADMIN_DEFAULT_PASSWORD": "securepassword",
                    }},
                    "depends_on": ["{data_storage_host}"],
                    "networks": ["{network_name}"],
                }}

                """
            )

        # MySQL Configuration (Production-Ready)
        if "mysql" in config["data_storage"]:
            if use_combined_metastore and metastore_type == "mysql":
                dbs: List[str] = [f"{project_name}_db", f"{project_name}_metastore", "mysql"]
            else:
                dbs: List[str] = [f"{project_name}_db", "mysql"]

            dbs: str = ",".join(dbs)

            settings.append(
                f"""
                MYSQL_DEFAULTS = {{
                    "container_name": "{data_storage_host}",
                    "image": "{data_storage_type}",
                    "restart": "always",
                    "ports": ["3306:3306"],
                    "environment": {{
                        "MYSQL_ROOT_PASSWORD": "root_securepassword",
                        "MYSQL_MULTIPLE_DATABASES": "{dbs}",
                    }},
                    "volumes": [
                        "{storage_volume}:/var/lib/mysql",
                        "./mysql/mysql-init.sh:/docker-entrypoint-initdb.d/mysql-init.sh",
                    ],
                    "networks": ["{network_name}"],
                    "healthcheck": {{
                        "test": ["CMD-SHELL", "mysqladmin ping -u admin -p securepassword"],
                        "interval": "10s",
                        "timeout": "5s",
                        "retries": 5,
                    }},
                    "command": [
                        "--sql-mode=STRICT_ALL_TABLES,NO_ENGINE_SUBSTITUTION",
                        "--character-set-server=utf8mb4",
                        "--collation-server=utf8mb4_unicode_ci",
                        "--max_connections=250",
                    ],
                }}

                PHPMYADMIN_DEFAULTS = {{
                    "container_name": "{project_name}_phpmyadmin",
                    "image": "phpmyadmin",
                    "restart": "always",
                    "ports": ["8081:80"],
                    "environment": {{
                        "PMA_HOST": "{data_storage_host}",
                        "MYSQL_ROOT_PASSWORD": "root_securepassword",
                        "PMA_USER": "admin",
                        "PMA_PASSWORD": "securepassword",
                    }},
                    "depends_on": ["{data_storage_host}"],
                    "networks": ["{network_name}"],
                }}

                """
            )

        settings.append("# Data Modeling Configuration")

        if "dbt" in config["data_modeling"]:
            settings.append(
                f"""
                DBT_DEFAULTS = {{
                    "container_name": "{project_name}_data_modeling",
                    "image": "{project_name}_data_modeling",
                    "build": {{
                        "context": "./dbt",
                        "dockerfile": "Dockerfile",
                    }},
                    "environment": {{
                        "PROJECT_NAME": "{project_name}",
                        "DBT_PROFILES_DIR": "/root/.dbt",
                        "DBT_TARGET": "dev",
                        "DB_USER": "admin",
                        "DB_PASSWORD": "securepassword",
                        "DB_NAME": "{project_name}_db",
                        "STORAGE_TYPE": "{data_storage_type}",
                        "DB_PORT": "{data_storage_port}",
                    }},
                    "volumes": [
                        "./dbt:/dbt",  # Ensure the dbt project is locally accessible
                        "~/.dbt:/root/.dbt",  # Persist dbt profiles
                    ],
                    "entrypoint": ["/bin/bash", "dbt-init.sh"],  # Ensure dbt initialization runs
                    "depends_on": ["{data_storage_host}"],
                    "networks": ["{network_name}"],
                }}

                """
            )

        if "sqlmesh" in config["data_modeling"]:
            settings.append(
                f"""
                SQLMESH_DEFAULTS = {{
                    "container_name": "{project_name}_data_modeling",
                    "image": "{project_name}_data_modeling",
                    "build": {{
                        "context": "./sql_mesh",
                        "dockerfile": "Dockerfile",
                    }},
                    "volumes": [
                        "./sql_mesh:/sql_mesh",
                    ],
                    "environment": {{
                        "SQLMESH_TARGET": "dev",
                        "DB_PORT": "{data_storage_port}",
                        "DB_USER": "admin",
                        "DB_PASSWORD": "securepassword",
                        "DB_NAME": "{project_name}_db",
                    }},
                    "entrypoint": ["/bin/bash", "sqlmesh-init.sh"],  # Ensure sqlmesh initialization runs
                    "depends_on": ["{data_storage_host}"],
                    "networks": ["{network_name}"],
                }}

                """
            )

        settings.append("# Orchestration Metastore Configuration (Separate DB)")

        # PostgreSQL Metastore (if selected)
        if metastore_type == "postgres" and not use_combined_metastore:
            settings.append(
                f"""
                {data_orchestration_tool.upper()}_METASTORE_DEFAULTS = {{
                    "container_name": "{project_name}_metastore",
                    "image": "postgres",
                    "restart": "always",
                    "ports": ["5432:5432"],
                    "environment": {{
                        "POSTGRES_USER": "admin",
                        "POSTGRES_PASSWORD": "securepassword",
                        "POSTGRES_DB": "{project_name}_metastore",
                    }},
                    "volumes": ["{metastore_volume}:/var/lib/postgresql/data"],
                    "networks": ["{network_name}"],
                    "healthcheck": {{
                        "test": ["CMD-SHELL", "pg_isready -U admin -d {project_name}_metastore"],
                        "interval": "10s",
                        "timeout": "5s",
                        "retries": 5,
                    }},
                }}

                PGADMIN_METASTORE_DEFAULTS = {{
                    "container_name": "{project_name}_metastore_pgadmin",
                    "image": "dpage/pgadmin4",
                    "restart": "always",
                    "ports": ["5050:80"],
                    "environment": {{
                        "PGADMIN_DEFAULT_EMAIL": "admin@admin.com",
                        "PGADMIN_DEFAULT_PASSWORD": "securepassword",
                    }},
                    "depends_on": ["{project_name}_metastore"],
                    "networks": ["{network_name}"],
                }}

                """
            )

        # MySQL Metastore (if selected)
        if config["data_orchestration"] == "airflow" and metastore_type == "mysql" and not use_combined_metastore:
            settings.append(
                f"""
                {data_orchestration_tool.upper()}_METASTORE_DEFAULTS = {{
                    "container_name": "{project_name}_metastore",
                    "image": "mysql",
                    "restart": "always",
                    "ports": ["3306:3306"],  # Uses a different external port
                    "environment": {{
                        "MYSQL_DATABASE": "{project_name}_metastore",
                        "MYSQL_USER": "admin",
                        "MYSQL_PASSWORD": "securepassword",
                        "MYSQL_ROOT_PASSWORD": "root_securepassword",
                    }},
                    "volumes": ["{metastore_volume}:/var/lib/mysql"],
                    "networks": ["{network_name}"],
                    "healthcheck": {{
                        "test": ["CMD-SHELL", "mysqladmin ping -h localhost"],
                        "interval": "10s",
                        "timeout": "5s",
                        "retries": 5,
                    }},
                }}

                PHPMYADMIN_METASTORE_DEFAULTS = {{
                    "container_name": "{project_name}_metastore_phpmyadmin",
                    "image": "phpmyadmin",
                    "restart": "always",
                    "ports": ["8081:80"],
                    "environment": {{
                        "PMA_HOST": "{project_name}_metastore",
                        "MYSQL_ROOT_PASSWORD": "root_securepassword",
                        "PMA_USER": "admin",
                        "PMA_PASSWORD": "securepassword",
                    }},
                    "depends_on": ["{project_name}_metastore"],
                    "networks": ["{network_name}"],
                }}

                """
            )

        settings.append("# Orchestration Configuration")

        # AIRFLOW CONFIGURATION
        if "airflow" in config["data_orchestration"]:
            celery_backend: str = f"redis://{project_name}_orchestration_redis:6379/0"

            # Determine metastore host
            metastore_host: str = f"{project_name}_metastore" if not use_combined_metastore else f"{project_name}_data_storage"
            sql_driver: str = ""

            # Determine proper SQLAlchemy driver
            if metastore_type == "postgres":
                sql_driver = "postgresql+psycopg2"
            elif metastore_type == "mysql":
                sql_driver = "mysql+pymysql"

            # Build SQLAlchemy connection string
            sql_conn: str = f"{sql_driver}://admin:securepassword@{metastore_host}:{metastore_port}/{project_name}_metastore"

            settings.append(
                f"""
                AIRFLOW_DEFAULTS = {{
                    "image": "apache/airflow:2.8.2",
                    "restart": "always",
                    "container_name": "{project_name}_orchestration",
                    "environment": {{
                        "AIRFLOW__CORE__EXECUTOR": "CeleryExecutor",
                        "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN": "{sql_conn}",
                        "AIRFLOW__CELERY__BROKER_URL": "{celery_backend}",
                        "AIRFLOW__CELERY__RESULT_BACKEND": "{celery_backend}",
                        "AIRFLOW__CORE__FERNET_KEY": "jLxr6Lv3aC4d_ZNKTsHa5ffUlvrA0687UrKbPlkwhQA=",
                        "AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION": "true",
                        "AIRFLOW__CORE__LOAD_EXAMPLES": "false",
                        "AIRFLOW__API__AUTH_BACKENDS": "airflow.api.auth.backend.basic_auth",
                        "DB_PORT": "{metastore_port}",
                        "DB_HOST": "{metastore_host}",
                        "DB_USER": "admin",
                        "DB_PASSWORD": "securepassword",
                        "DB_NAME": "{project_name}_metastore",
                        "ENV_MODE": "dev", # Remove this in production
                    }},
                    "volumes": [
                        "./airflow/dags:/opt/airflow/dags",
                        "./airflow/logs:/opt/airflow/logs",
                        "./airflow/plugins:/opt/airflow/plugins",
                        "./airflow/airflow-init.sh:/entrypoint.sh",
                    ],
                    "entrypoint": ["/bin/bash", "/entrypoint.sh"],
                    "networks": ["{network_name}"],
                    "depends_on": ["{metastore_host}", "{project_name}_orchestration_redis"],
                    "command": ["standalone"],
                }}

                AIRFLOW_WEBSERVER = {{
                    **AIRFLOW_DEFAULTS,
                    "container_name": "{project_name}_orchestration_webserver",
                    "depends_on": ["{project_name}_orchestration"],
                    "ports": ["8080:8080"],
                    "command": ["webserver"],
                }}

                AIRFLOW_SCHEDULER = {{
                    **AIRFLOW_DEFAULTS,
                    "container_name": "{project_name}_orchestration_scheduler",
                    "depends_on": ["{project_name}_orchestration"],
                    "command": ["scheduler"],
                }}

                AIRFLOW_WORKER = {{
                    **AIRFLOW_DEFAULTS,
                    "container_name": "{project_name}_orchestration_worker",
                    "depends_on": ["{project_name}_orchestration"],
                    "command": ["celery", "worker"],
                }}

                AIRFLOW_TRIGGERER = {{
                    **AIRFLOW_DEFAULTS,
                    "container_name": "{project_name}_orchestration_triggerer",
                    "depends_on": ["{project_name}_data_storage", "{project_name}_orchestration_redis"],
                    "command": ["triggerer"],
                }}

                REDIS_DEFAULTS = {{
                    "container_name": "{project_name}_orchestration_redis",
                    "image": "redis",
                    "restart": "always",
                    "ports": ["6379:6379"],
                    "networks": ["{network_name}"],
                }}
                """
            )

        # DAGSTER CONFIGURATION
        if "dagster" in config["data_orchestration"]:
            metastore_container: str = ""

            # Determine which container to use as the metastore
            if config["data_storage"] == "postgresql":
                metastore_container = f"{project_name}_data_storage"
            else:
                metastore_container = f"{project_name}_metastore"

            settings.append(
                f"""
                DAGSTER_WEBSERVER_DEFAULTS = {{
                    "container_name": "{project_name}_dagster_webserver",
                    "build": {{
                        "context": "./dagster",
                        "dockerfile": "Dockerfile",
                    }},
                    "restart": "always",
                    "ports": ["3000:3000"],
                    "environment": {{
                        "DAGSTER_HOME": "/opt/dagster/app",
                        "DAGSTER_POSTGRES_DB": "{project_name}_metastore",
                        "DAGSTER_POSTGRES_USER": "admin",
                        "DAGSTER_POSTGRES_PASSWORD": "securepassword",
                        "DAGSTER_POSTGRES_HOST": "{metastore_container}",
                    }},
                    "volumes": ["./dagster:/opt/dagster/app"],
                    "networks": ["{network_name}"],
                    "depends_on": {{
                        "{metastore_container}": {{
                            "condition": "service_healthy"
                        }}
                    }},
                    "healthcheck": {{
                        "test": ["CMD", "dagster-daemon", "healthcheck"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 5
                    }},
                    "command": ["dagit", "-h", "0.0.0.0", "-p", "3000"]
                }}

                DAGSTER_DAEMON_DEFAULTS = {{
                    "container_name": "{project_name}_dagster_daemon",
                    "build": {{
                        "context": "./dagster",
                        "dockerfile": "Dockerfile",
                    }},
                    "restart": "always",
                    "environment": {{
                        "DAGSTER_HOME": "/opt/dagster/app",
                        "DAGSTER_POSTGRES_DB": "{project_name}_metastore",
                        "DAGSTER_POSTGRES_USER": "admin",
                        "DAGSTER_POSTGRES_PASSWORD": "securepassword",
                        "DAGSTER_POSTGRES_HOST": "{metastore_container}",
                    }},
                    "volumes": ["./dagster:/opt/dagster/app"],
                    "networks": ["{network_name}"],
                    "depends_on": {{
                        "{metastore_container}": {{
                            "condition": "service_healthy"
                        }}
                    }},
                    "healthcheck": {{
                        "test": ["CMD", "dagster-daemon", "healthcheck"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 5
                    }},
                    "command": ["dagster-daemon", "run"]
                }}
                """
            )

        # Write to file properly with correct spacing
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dedent(summary))
            f.write(dedent(output_project_name))
            f.write(dedent(network))
            f.write(dedent(volumes))
            for setting in settings:
                f.write(dedent(setting))
