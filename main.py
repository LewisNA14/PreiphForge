"""
@file main.py
@brief CLI entry point. Reads a JSON config, validates with Pydantic, renders a C header via Jinja2.
@author L. Nicholson-Andrews (lewisnich01@outlook.com)
"""

import json
import sys
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pydantic import BaseModel, Field, ValidationError

#-------------------------------------------------------------------------------------
# Models 

class Register(BaseModel):
    offset: int
    name: str = Field(pattern="^[A-Za-z_][A-Za-z0-9_]*$")


class Peripheral(BaseModel):
    name: str = Field(...)
    base_address: int
    size: int
    enabled: bool
    registers: list[Register]

#-------------------------------------------------------------------------------------
# Core logic (no CLI concern here)

def load_config(config_path: Path) -> Peripheral:
    """Read and validate the JSON config file."""
    try:
        with open(config_path) as f:
            data = json.load(f)
        return Peripheral(**data)
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON: {e}")
    except ValidationError as e:
        raise click.ClickException(f"Config validation failed:\n{e}")


def render_template(peripheral: Peripheral, template_dir: Path, template_name: str) -> str:
    """Render the Jinja2 template with the validated peripheral data."""
    try:
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template(template_name)
        return template.render(peripheral=peripheral)
    except TemplateNotFound:
        raise click.ClickException(f"Template '{template_name}' not found in '{template_dir}'")


def write_output(content: str, output_path: Path) -> None:
    """Write rendered content to the output file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(content)


#-------------------------------------------------------------------------------------
# CLI - Using Click Library

@click.command()
@click.argument("config", type=click.Path(exists=True, readable=True, path_type=Path))
@click.option(
    "--template", "-t",
    default="UART_periph_template.h.jinja",
    show_default=True,
    help="Jinja2 template filename (looked up inside --template-dir).",
)
@click.option(
    "--template-dir", "-d",
    default="templates",
    show_default=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory containing Jinja2 templates.",
)
@click.option(
    "--output", "-o",
    default="output/out.h",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to write the generated header file.",
)
@click.option("--verbose", "-v", is_flag=True, help="Print extra info during generation.")
def generate(config, template, template_dir, output, verbose):
    """Generate a C peripheral header from a JSON config file.

    CONFIG is the path to your JSON peripheral definition.

    Example:

        periforge inputs/uart.json --output output/UART0.h
    """
    if verbose:
        click.echo(f"  Config      : {config}")
        click.echo(f"  Template    : {template_dir / template}")
        click.echo(f"  Output      : {output}")

    peripheral = load_config(config)

    if verbose:
        click.echo(f"  Peripheral  : {peripheral.name} @ {hex(peripheral.base_address)}")
        click.echo(f"  Registers   : {[r.name for r in peripheral.registers]}")

    content = render_template(peripheral, template_dir, template)
    write_output(content, output)

    click.secho(f"✓ Generated: {output}", fg="green")


if __name__ == "__main__":
    generate()