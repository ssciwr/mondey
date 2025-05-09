"""
Command-line interface for the ImportManager.

This module provides a command-line interface for running import operations
using the ImportManager class.
"""

import asyncio
import logging
import sys
from pathlib import Path

import click

from mondey_backend.import_data.manager import ImportManager
from mondey_backend.import_data.manager.import_manager import ImportPaths


@click.group()
@click.option("--debug/--no-debug", default=False, help="Enable debug logging")
@click.option(
    "--mondey-db",
    type=click.Path(exists=False),
    help="Path to the Mondey database",
)
@click.option(
    "--current-db",
    type=click.Path(exists=False),
    help="Path to the current database",
)
@click.option(
    "--users-db",
    type=click.Path(exists=False),
    help="Path to the users database",
)
@click.pass_context
def cli(ctx, debug, mondey_db, current_db, users_db):
    """Import data into the Mondey system."""
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Create ImportManager
    ctx.obj = {
        "manager": ImportManager(
            mondey_db_path=Path(mondey_db) if mondey_db else None,
            current_db_path=Path(current_db) if current_db else None,
            users_db_path=Path(users_db) if users_db else None,
            debug=debug,
        )
    }


@cli.command()
@click.option(
    "--labels",
    type=click.Path(exists=True),
    help="Path to the labels CSV file",
)
@click.option(
    "--data",
    type=click.Path(exists=True),
    help="Path to the data CSV file",
)
@click.option(
    "--questions",
    type=click.Path(exists=True),
    help="Path to the questions configuration CSV file",
)
@click.option(
    "--milestones",
    type=click.Path(exists=True),
    help="Path to the milestones metadata CSV file",
)
@click.option(
    "--confirm/--no-confirm",
    default=True,
    help="Confirm before running import",
)
@click.pass_context
def full_import(ctx, labels, data, questions, milestones, confirm):
    """Run a full import of all data."""
    manager = ctx.obj["manager"]
    
    # Update paths if provided
    if any([labels, data, questions, milestones]):
        import_paths = ImportPaths(
            labels_path=Path(labels) if labels else manager.import_paths.labels_path,
            data_path=Path(data) if data else manager.import_paths.data_path,
            questions_configured_path=Path(questions) if questions else manager.import_paths.questions_configured_path,
            milestones_metadata_path=Path(milestones) if milestones else manager.import_paths.milestones_metadata_path,
        )
        manager.import_paths = import_paths
    
    # Confirm before running
    if confirm:
        click.echo("This will import all data into the Mondey system.")
        click.echo(f"Labels: {manager.import_paths.labels_path}")
        click.echo(f"Data: {manager.import_paths.data_path}")
        click.echo(f"Questions: {manager.import_paths.questions_configured_path}")
        click.echo(f"Milestones: {manager.import_paths.milestones_metadata_path}")
        click.echo(f"Mondey DB: {manager.mondey_db_path}")
        click.echo(f"Current DB: {manager.current_db_path}")
        click.echo(f"Users DB: {manager.users_db_path}")
        
        if not click.confirm("Do you want to continue?"):
            click.echo("Import cancelled.")
            return
    
    # Run import
    asyncio.run(manager.run_full_import())
    click.echo("Import completed successfully.")


@cli.command()
@click.option(
    "--additional-data",
    type=click.Path(exists=True),
    required=True,
    help="Path to the additional data CSV file",
)
@click.option(
    "--confirm/--no-confirm",
    default=True,
    help="Confirm before running import",
)
@click.pass_context
def additional_import(ctx, additional_data, confirm):
    """Run import of additional data."""
    manager = ctx.obj["manager"]
    
    # Update additional data path
    manager.import_paths.additional_data_path = Path(additional_data)
    
    # Confirm before running
    if confirm:
        click.echo("This will import additional data into the Mondey system.")
        click.echo(f"Additional data: {manager.import_paths.additional_data_path}")
        click.echo(f"Current DB: {manager.current_db_path}")
        click.echo(f"Users DB: {manager.users_db_path}")
        
        if not click.confirm("Do you want to continue?"):
            click.echo("Import cancelled.")
            return
    
    # Run import
    asyncio.run(manager.run_additional_data_import())
    click.echo("Additional data import completed successfully.")


@cli.command()
@click.option(
    "--confirm/--no-confirm",
    default=True,
    help="Confirm before clearing users database",
)
@click.pass_context
def clear_users(ctx, confirm):
    """Clear all data from the users database."""
    manager = ctx.obj["manager"]
    
    # Confirm before running
    if confirm:
        click.echo("This will clear all data from the users database.")
        click.echo(f"Users DB: {manager.users_db_path}")
        
        if not click.confirm("Do you want to continue?"):
            click.echo("Operation cancelled.")
            return
    
    # Run clear
    result = asyncio.run(manager.clear_users_database())
    
    if result:
        click.echo("Users database cleared successfully.")
    else:
        click.echo("No users were deleted or an error occurred.")


if __name__ == "__main__":
    cli(obj={})
