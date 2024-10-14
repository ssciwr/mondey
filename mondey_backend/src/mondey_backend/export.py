from __future__ import annotations

import json

import click
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from .main import create_app


@click.command()
@click.argument("filename", default="openapi.json")
def export_openapi_json(filename: str) -> None:
    app = create_app()
    click.echo(f"Exporting MONDEY OpenAPI spec to {filename}...", nl=False)
    # simplify route names to get less redundantly verbose API function names
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name
    with open(filename, "w") as f:
        json.dump(
            get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes,
                separate_input_output_schemas=False,
            ),
            f,
        )
    click.echo("done.")
