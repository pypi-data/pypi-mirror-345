from typing import Dict


SUPPORTED_TOOLS: Dict = {
    "data_storage": {
        "PostgreSQL": "postgresql",
        "MySQL": "mysql",
    },
    "data_modeling": {
        "dbt": "dbt",
        "SQL Mesh": "sqlmesh",
    },
    "data_orchestration": {
        "Airflow": {
            "tool_name": "airflow",
            "metastore": ["postgresql", "mysql",],
        },
        "Dagster": {
            "tool_name": "dagster",
            "metastore": ["postgresql",],
        },
    },
}
