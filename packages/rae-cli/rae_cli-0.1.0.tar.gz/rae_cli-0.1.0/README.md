<!-- Badges: only visible once published to real PyPI -->
<!-- ![PyPI Version](https://img.shields.io/pypi/v/rae) -->
<!-- ![Python Versions](https://img.shields.io/pypi/pyversions/rae) -->
<!-- ![Downloads](https://img.shields.io/pypi/dm/rae) -->


# RAE - Rapid Analytics Engineering

*Perfectly imperfect, for she was a Wildflower*

**RAE** is the first opinionated framework that is purpose-built for the **Analytics Engineering** community — inspired by the likes of web frameworks such as **Django**, **Flask** and **NestJS**, but reimagined for data projects - Specifically Analytics Engineering projects and their required tool/stack.

**RAE** empowers individual engineers and teams to **rapidly scaffold a modern analytics engineering stack** with nothing more than a few responses to CLI prompts. From zero to fully containerized infrastructure in minutes, RAE abstracts away the boilerplate so you can focus on **what matters most: modeling, orchestrating, and delivering data.**

---

## What RAE Does

### Scaffold Tool Docker Configurations
Spin up a project with plug-and-play support for essential data tools:

- **Data Storage**:
  - PostgreSQL
  - MySQL  
- **Data Modeling**:
  - dbt
  - SQL Mesh  
- **Orchestration**:
  - Airflow
  - Dagster

### Auto-Generate `settings.py`
A clean and extensible settings file inspired by Django — making it easy to pass environment-specific values (ports, credentials, container names, etc.) to every component of your stack.

### Auto-Generate `docker-compose.yml`
- Connect all services via a shared Docker network.

---

Frameworks aren't just for web and mobile engineers anymore.
**RAE** gives Analytics Engineers the tools to build, connect and orchestrate their data stack with ease.

Build like a developer. Deploy like an engineer. Let **RAE** compose your analytics stack.

---

## Who Is RAE For?

- Analytics Engineers who want to quickly scaffold their required infrastructure.
- Data Engineers who need to tie various tools together.
- Data Scientists who have a need for a data tool stack.
- Individual developers and anyone learning to use analytics/data engineering tools.
- Teams that want standardization and clarity across their data stack.

---

## How to use RAE

### System Dependencies

| Tool            | Required Version | Notes                                                                 |
|-----------------|------------------|-----------------------------------------------------------------------|
| **Python**      | 3.8+             | Required for the RAE CLI tool                                         |
| **Docker Desktop**      | Latest           | Docker Desktop (macOS/Windows) or Docker Engine (Linux)               |
| **Shell**       | bash / zsh / PowerShell | Used to run CLI and Docker commands                             |
| **Web Browser** | Any modern browser | `Google Chrome` recommended for container-based UIs (e.g. Airflow)    |

### CLI Setup Steps

#### 1. Create a Virtual Environment

| OS            | Command                          |
|---------------|----------------------------------|
| macOS/Linux   | `python3 -m venv local-env`      |
| Windows       | `py -m venv local-env`           |

---

#### 2. Activate the Virtual Environment

| OS                  | Command                                 |
|---------------------|-----------------------------------------|
| macOS/Linux (bash/zsh) | `source local-env/bin/activate`        |
| Windows (CMD)       | `local-env\Scripts\activate.bat`        |
| Windows (PowerShell)| `local-env\Scripts\Activate.ps1`        |

#### 3. Install RAE CLI:
```bash
pip install rae
```

#### 4. Initialize your project:
```bash
rae init
```

This will take you through a series of prompts and then generate the `project_config.json` and `settings.py` files.

After this command completes you will be left with the following project structure:
```bash
├── rae
│   └── src
│       ├── airflow
│       │   └── airflow-init.sh
│       ├── dbt
│       │   ├── analyses
│       │   ├── macros
│       │   ├── models
│       │   ├── seeds
│       │   ├── snapshots
│       │   ├── tests
│       │   ├── dbt-init.sh
│       │   ├── dbt.sh
│       │   ├── dbt_project.yml
│       │   └── Dockerfile
│       ├── docker-compose.yml
│       ├── postgres
│       │   └── postgres-init.sh
│       └── settings
│           ├── project_config.json
│           └── settings.py
```

*The above is just an example and assumes you selected postgres as your data storage, dbt as your data modeling and airflow as your orchestration with postgres as the metastore.*

#### 5. Open your settings file - `{project_name}/src/settings/settings.py`
    - You need to populate this file with your specific credentials
        - `data_storage` (PostgreSQL or MySQL)
        - `data_modeling` (dbt or SQL Mesh)
        - `data_orchestration` (Airflow or Dagster)
    - If you do not do this, the project will be usable, but the project's containers will be built with default values and will NOT BE production ready nor secure.
    
**You are responsible for ensuring your project is secure, is setup properly and is ready for deployment!**

#### 6. Generate your docker compose file:
1. cd into your project directory:
```bash
cd {project_name}/src
```
2. generate your compose file:
```bash
rae generate-compose-file
```

3. generate docker-compose file without changing directories:
```bash
rae generate-compose-file --project-name {project_name}
```

#### 7. Run your project's ddocker containers:
*Docker must be running on your host machine or this command will fail*
*So make sure you have Docker Desktop open on your machine!*
```bash
cd {project_name}/src
```
Then simply start the containers:
```bash
docker-compose up -d
```

This will run the docker containers for each service and link them via a docker network. The process allows for each container to communicate with one another while still ensuring all tools operate in an isolated state.

---

# Current State of Project

## Current Tasks
1. Upload to PyPi
  - Change name of project to `rae`
  - Manually test the following:
    - pip install from PyPi
      - docker containers run
        - connect?
        - network?
        - initialize?

## To Do
```bash
1. Add secondary test coverage to the project:
  - src/cli.py
  - src/data_modeling/dbt_modeling
  - src/data_modeling/sql_mesh_modeling
  - src/data_orchestration/airflow_orchestration.py
  - src/data_orchestration/dagster_orchestration.py
  - src/data_storage/mysql_storage.py
  - src/data_storage/postgresql_storage.py
  - src/generators/docker_compose_generator.py
  
2. Continue iterating on test coverage
  - src/managers/data_modeling_manager.py
  - src/managers/data_orchestration_manager.py
  - src/managers/data_storage_manager.py
  - src/managers/settings_manager.py
  - src/utility/base_manager.py
  - src/utility/base_tool.py
  - src/utility/dockerfile_writer.py
  - src/utility/indented_dumper.py
  - src/utility/shell_script_writer.py
  - src/utility/supported_tools.py
  - src/main.py

3. Add support for additional data storage tools:
  - Snowflake
  - DuckDB?
  - SQL Server?
  - Databricks
    - AWS S3
    - Google Cloud Storage
    - Azure Blob Storage

4. Add support to allow users to scaffold single applications or custom lists of applications
  - Scenarios:
    - user only needs a data modeling tool
    - user only needs a data modeling tool and a data storage tool
    - user only needs an orchestration tool
    - etc
  - Intent:
    - To allow greater flexibility and provide a wider use-case for the CLI
```

  # Project's Structure
 Below is the project structure:
 ```bash
└── rapid_analytics_engineering
    ├── cli
    │   └── cli.py
    ├── data_modeling
    │   ├── dbt_modeling.py
    │   └── sql_mesh_modeling.py
    ├── data_orchestration
    │   ├── airflow_orchestration.py
    │   └── dagster_orchestration.py
    ├── data_storage
    │   ├── mysql_storage.py
    │   └── postgresql_storage.py
    ├── easter_eggs
    │   └── wildflower.py
    ├── generators
    │   └── docker_compose_generator.py
    ├── main.py
    ├── managers
    │   ├── data_modeling_manager.py
    │   ├── data_orchestration_manager.py
    │   ├── data_storage_manager.py
    │   └── settings_manager.py
    └── utility
        ├── base_manager.py
        ├── base_tool.py
        ├── dockerfile_writer.py
        ├── indented_dumper.py
        ├── shell_script_writer.py
        ├── supported_tools.py
        └── yaml_configs
            └── dbt_project.yml
 ```
  