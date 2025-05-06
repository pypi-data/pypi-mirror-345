import click

from rapid_analytics_engineering.cli.cli import RaeCLI

rae_cli: RaeCLI = RaeCLI()


@click.group()
def cli():
    """RAE CLI - Scaffold your analytics engineering tool stack."""
    pass


@cli.command()
def init():
    """Initialize an analytics project."""
    rae_cli.init_project()


@cli.command(name="generate-compose-file")
@click.option("--project-name", default=None, help="The name of the user's project directory.")
def generate_compose_file(project_name):
    """Generate configuration files."""
    rae_cli.generate_docker_compose(project_name)


@cli.command()
def validate_settings():
    """Validate your project's settings."""
    rae_cli.validate_settings()


@cli.command()
def list_services():
    """List all the configured services for your project."""
    rae_cli.list_services()


@cli.command()
def show_config():
    """
    Show your current selected configuration options.
    This lists the tools you selected via the CLI prompts and is equivalent to your project_config.json file.
    """
    rae_cli.show_config()


@cli.command()
@click.argument("--service-name")
def add_service(service_name):
    """
    Add a new service to the configuration file (project_config.json).
    In this context a service is a tool like dbt, postgres, airflow, etc.
    """
    rae_cli.add_service(service_name)


@cli.command()
@click.argument("--service-name")
def remove_service(service_name):
    """
    Remove an existing service/tool from the configuration.
    In this context a service is a tool like dbt, postgres, airflow, etc.
    """
    rae_cli.remove_service(service_name)


@cli.command()
@click.option("--force", is_flag=True, help="Skip confirmation and forcefully reset the project configuration.")
def reset_config(force):
    """
    Reset the project configuration.

    By default, you will be prompted for confirmation before resetting the configuration.
    Use --force to skip the confirmation and reset immediately.
    """
    rae_cli.reset_config(force)


@cli.command(hidden=True)
def clean_project():
    """Clean up project-related directories."""
    rae_cli.run_cleanup()


# Easter Eggs
@cli.command(hidden=True, name="wildflower")
def draw_wildflower():
    rae_cli.draw_wildflower()


if __name__ == "__main__":
    cli()
