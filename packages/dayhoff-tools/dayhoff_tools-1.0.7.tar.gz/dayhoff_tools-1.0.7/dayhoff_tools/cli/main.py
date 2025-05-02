"""Entry file for the CLI, which aggregates and aliases all commands."""

import typer
from dayhoff_tools.cli.cloud_commands import aws_app, gcp_app
from dayhoff_tools.cli.utility_commands import (
    add_to_warehouse_typer,
    build_and_upload_wheel,
    delete_local_branch,
    get_ancestry,
    import_from_warehouse_typer,
    rebuild_devcontainer_file,
    test_github_actions_locally,
    update_dayhoff_tools,
)

app = typer.Typer()

# Utility commands
app.command("clean")(delete_local_branch)
app.command("gha")(test_github_actions_locally)
app.command("rebuild")(rebuild_devcontainer_file)
app.command("update")(update_dayhoff_tools)
app.command("wadd")(add_to_warehouse_typer)
app.command("wancestry")(get_ancestry)
app.command("wimport")(import_from_warehouse_typer)

# Cloud commands
app.add_typer(gcp_app, name="gcp", help="Manage GCP authentication and impersonation.")
app.add_typer(aws_app, name="aws", help="Manage AWS SSO authentication.")


@app.command("wheel")
def build_and_upload_wheel_command(
    bump: str = typer.Option(
        "patch",
        "--bump",
        "-b",
        help="Which part of the version to bump: 'major', 'minor', or 'patch'.",
        case_sensitive=False,
    )
):
    """Build wheel, bump version, and upload to PyPI."""
    build_and_upload_wheel(bump_part=bump)


# Use lazy loading for slow-loading swarm commands
@app.command("reset")
def reset_wrapper(
    firestore_collection: str = typer.Option(prompt=True),
    old_status: str = typer.Option(default="failed", prompt=True),
    new_status: str = typer.Option(default="available", prompt=True),
    delete_old: bool = typer.Option(default=True, prompt=True),
):
    """Find all the documents in the database with a given status, and
    make a new document with the same name and a new status."""
    from dayhoff_tools.cli.swarm_commands import reset_failed_cards

    reset_failed_cards(firestore_collection, old_status, new_status, delete_old)


@app.command("zombie")
def zombie_wrapper(
    firestore_collection: str = typer.Option(prompt=True),
    delete_old: bool = typer.Option(default=True, prompt=True),
    minutes_threshold: int = typer.Option(default=60, prompt=True),
):
    """Find all the documents in the database with status "assigned", and "last_updated"
    older than a specified threshold, and make a new "available" document for them."""
    from dayhoff_tools.cli.swarm_commands import reset_zombie_cards

    reset_zombie_cards(firestore_collection, delete_old, minutes_threshold)


@app.command("status")
def status_wrapper(
    firestore_collection: str = typer.Argument(),
):
    """Count the various statuses of items in a given collection."""
    from dayhoff_tools.cli.swarm_commands import get_firestore_collection_status

    get_firestore_collection_status(firestore_collection)


# Deployment commands - use lazy loading but preserve argument passing
@app.command("deploy")
def deploy_command(
    mode: str = typer.Argument(help="Deployment mode. Options: local, shell, batch"),
    config_path: str = typer.Argument(help="Path to the YAML configuration file"),
):
    """Unified deployment command."""
    from dayhoff_tools.deployment.base import deploy

    deploy(mode, config_path)


@app.command("job")
def run_job_command(
    mode: str = typer.Argument(
        default="setup_and_execute",
        help="Mode to run in: setup (setup only), execute (execute only), or setup_and_execute (both)",
    )
):
    """Run a job."""
    from dayhoff_tools.deployment.job_runner import run_job

    run_job(mode)


if __name__ == "__main__":
    app()
