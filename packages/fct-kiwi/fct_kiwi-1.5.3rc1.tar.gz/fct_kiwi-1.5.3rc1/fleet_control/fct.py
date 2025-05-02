#!/usr/bin/env python3
# =============================================================================
"""Balena Vars

Author:
    Juan Pablo Castillo - juan.castillo@kiwibot.com
"""
# =============================================================================
import click
import json
from typing import List, Dict, Optional, Tuple
from fleet_control.resources.commands import change, clone, purge, get, delete, move, schedule, initialize, rename
from fleet_control.utils.utils import *

@click.group()
def cli():
    """Balena device configuration management tool."""
    pass


@cli.command(name="change")
@click.argument("variables", type=str, required=False)
@click.argument("targets", type=str, nargs=-1)
@click.option("--file", type=click.Path(exists=True, readable=True), help="Path to a file containing variables.")
def _change(variables, targets: List[str], file):
    """
    Change or create specified variable(s) to TARGET(s).

    \b
    VARIABLES: Separated by spaces in the form "var1=value1=service1 var2=value2=service2"
    TARGETS: One or more target device IDs (format: 4X000)
    
    \b
    Example: fct change 'NODE_WEATHER_DEBUG=0=*' Staging4_x 4D164
    Example with fleets: fct change 'NODE_WEATHER_DEBUG=0=*' Staging4_x 4D164
    Example with file: fct change --file variables.txt '' 4D163 4D164
    """

    if file:
        variables = load_json(file)

    if not variables:
        click.echo("Error: No variables provided.", err=True)
        return

    change(variables, targets)


@cli.command(name="clone")
@click.option(
    "--exclude",
    type=str,
    help='Variables to exclude, must be in the format "var1 var2"',
)
@click.argument("source", type=str)
@click.argument("targets", type=str, nargs=-1)
def _clone(source: str, targets: tuple, exclude: str):
    """
    Clone configuration from SOURCE to TARGET(s).

    \b
    SOURCE: Either a device ID (format: 4X000) or a fleet name.
    TARGETS: One or more target device IDs (format: 4X000) or fleets.

    \b
    Example: fct clone 4E288 4D163 4D164
    Example with fleet: fct clone Staging4_x 4D163
    Example with fleet: fct clone Staging4_x fleet_name
    """
    clone(source, targets, exclude)


@cli.command(name="purge")
@click.option(
    "--exclude",
    type=str,
    help='Variables to exclude, must be in the format "var1 var2"',
)
@click.argument("targets", type=str, nargs=-1)
def _purge(targets: List[str], exclude: str):
    """
    Purge all custom variables in TARGET device(s).

    \b
    TARGETS: One or more target device IDs (format: 4X000).

    \b
    Example: fct purge 4E288 4D163 4D164
    """
    purge(targets, exclude)


@cli.command(name="get")
@click.argument("target_id", type=str)
@click.argument("variable_name", type=str, required=False)
@click.option("--output", "-o", type=click.Path(writable=True), help="File to save the output.")
@click.option("--custom", "-c", is_flag=True, help="Return all custom vars")
@click.option("--all-vars", "-a", is_flag=True, help="Return all device + fleet vars")
def _get(target_id: str, variable_name: str, output: str, custom: bool, all_vars: bool):
    """
    Fetch variable value for a device.

    \b
    TARGET_ID: Device ID (format: 4X000).

    \b
    Example: fct get 4E288 UAVCAN_CHASSIS_CURRENT_T2
    Example with file output: fct get --output result.json 4E288
    """

    if variable_name is None and not all_vars and not output and not custom:
        click.echo(f"Error: No variables provided", err=True)
        exit(1)
    if output:
        all_vars = True
    result = get(target_id, variable_name, custom, all_vars)
    if isinstance(result, str):
        print(f"Value for variable {variable_name} is: {result}")
    elif isinstance(result, dict):
        print(json.dumps(result, indent=2, sort_keys=True))
    if output:
        with open(output, "w") as f:
            json.dump(result, f, indent=4, sort_keys=True)
        click.echo(f"Result saved to {output}")


@cli.command(name="delete")
@click.argument("variables", type=str, required=False)
@click.argument("targets", type=str, nargs=-1)
@click.option("--file", type=click.Path(exists=True, readable=True), help="Path to a file containing variables.")
def _delete(variables, targets: List[str], file):
    """
    Delete the overwritten value for the specified variable(s) on the TARGET device(s).

    \b
    VARIABLES: Separated by spaces in the form "var1=value1=service1 var2=value2=service2"
    TARGETS: One or more target device IDs (format: 4X000)

    \b
    Example: fct delete 'NODE_WEATHER_DEBUG=0=*' 4D163 4D164
    Example with file: fct delete --file variables.txt '' 4D163 4D164
    """

    if file:
        variables = load_json(file)

    if not variables:
        click.echo("Error: No variables provided.", err=True)
        return
    delete(variables, targets)


@cli.command(name="move")
@click.option("--keep-vars", "-k", is_flag=True, help="keep custom device vars")
@click.option("--keep-service-vars", "-s", is_flag=True, help="keep custom device and service vars")
@click.option("--clone", "-c", is_flag=True, help="keep custom and previous fleet vars")
@click.option("--semver", "-p", type=str, help="pin to specific release (format: 1.3.11+rev87)")
@click.argument("fleet", type=str)
@click.argument("targets", type=str, nargs=-1)
def _move(fleet: str, targets: tuple, keep_vars: bool, keep_service_vars: bool, clone: bool, semver: str):
    """
    Move target(s) from its fleet to specified FLEET.

    \b
    FLEET: Chosen fleet's name (i.e: Production4_x).
    TARGETS: One or more target device IDs (format: 4X000).

    \b
    Example: fct move Staging4_x 4E288 4D163 4D164
    """
    move(fleet, targets, keep_vars, keep_service_vars, clone, semver)


@cli.command(name="schedule")
@click.option("--file", type=click.Path(exists=True), help="File with the targets and variables to change.")
@click.option(
    "--date",
    default=(datetime.datetime.now() + datetime.timedelta(days=1))
    .replace(hour=3, minute=0, second=0, microsecond=0)
    .strftime("%Y-%m-%d %H:%M:%S"),
    help="The date string to convert (e.g., '2024-11-25 15:30:00') [default: Next day at 3am]",
    show_default=False,
)
@click.option(
    "--format", "date_format", default="%Y-%m-%d %H:%M:%S", help="The format of the date string", show_default=True
)
@click.option(
    "--tz",
    # type=click.Choice(pytz.common_timezones),
    default="America/Bogota",
    help="The timezone for the schedule date",
    show_default=True,
)
@click.argument("variables", required=False)
@click.argument("targets", nargs=-1, required=False)
def _schedule(file, date, date_format, tz, variables, targets):
    """
    Creates a Google Cloud Task to send an HTTP POST request with variables to change in some targets to a Google Pub/Sub topic at a specified time.

    \b
    VARIABLES: must be in the format 'variable1=value=service'. Optional if using --file flag.
    TARGETS: to apply the changes to separated by spaces. Optional if using --file flag.

    \b
    Example: fct schedule --date '2025-02-25 12:06:00' 'WEATHER_NODE_DEBUG=0=main' 4B058 4D163
    Example: fct schedule --file vars.json --date '2025-02-25 12:06:00' '' 4B058
    """
    schedule(file, date, date_format, tz, variables, targets)

@cli.command(name="initialize")
@click.argument("fleet", type=str)
@click.argument("target", type=str)
def _initialize(fleet: str, target: str):
    """
    Initialize TARGET with previous device tags, remove old device, delete default config variables, and move to specified FLEET.

    \b
    FLEET: Chosen fleet's name (i.e: Production4_x).
    TARGET: Target device ID (format: 4X000).

    \b
    Example: fct initialize Staging4_x 4E288
    """
    initialize(target, fleet)

@cli.command(name="rename")
@click.argument("target", type=str)
@click.argument("new_id", type=str)
@click.option("--version", "-v", type=str, help="Overwrite tags with tags from configuration file for version")
def _rename(target: str, new_id: str, version: str):
    """
    Rename TARGET with new ID. Optional new tags for corresponding version read from configuration file.

    \b
    TARGET: Target device ID (format: 4X000).
    NEW_ID: New device ID (format: 4X000).

    \b
    Example: fct rename 4F407 4F265
    Example: fct rename --version 4.3F 4F407 4F265
    """
    rename(target, new_id, version=version)

if __name__ == "__main__":
    cli()
