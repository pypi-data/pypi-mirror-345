#!/usr/bin/env python3
# =============================================================================
"""Balena Vars

Author:
    Juan Pablo Castillo - juan.castillo@kiwibot.com
"""
# =============================================================================

import balena
import os
import re
import click
from typing import List, Dict, Optional, Tuple
from fleet_control.utils.utils import *
from fleet_control.resources.classes import *


def delete_variables(
    target_device: balena.types.models.TypeDevice,
    env_vars: Dict[str, str] | None = None,
    service_vars: Dict[str, str] | None = None,
    service: int = 0,
    exclude=None,
) -> None:
    """Update device variables with source variables."""
    device_id = target_device["id"]
    device_name = target_device.get("device_name", "Unknown")

    if exclude is None:
        exclude = set()
    exclude.add("BOT_ID")

    # Update environment variables
    if env_vars:
        for var_name in env_vars:
            if var_name in exclude:
                continue
            balena_sdk.models.device.env_var.remove(device_id, var_name)
            print(f"Variable {var_name} deleted for device {device_name}")

    # Update service variables
    if service_vars:
        for var_name in service_vars:
            if var_name in exclude:
                continue
            balena_sdk.models.device.service_var.remove(target_device["uuid"], service, var_name)
            print(f"Service variable {var_name} deleted for device {device_name}")


def update_variables(
    target: balena.types.models.TypeDevice | balena.types.models.TypeApplication | Device | Application,
    source_env_vars: Dict[str, str],
    source_service_vars: Dict[str, str],
    exclude=None,
    delete_custom: bool = False,
    turn_off_nodes: bool = False,
) -> None:
    """Update device or application variables with source variables.

    Args:
        target: Either a device or application object, or a Device/Application instance
        source_env_vars: Dictionary of environment variables to set
        source_service_vars: Dictionary of service variables to set
        exclude: List of variable names to exclude from updates
        delete_custom: Whether to delete custom variables
        turn_off_nodes: Whether to turn off nodes not present in source
    """
    # Create target object if a raw balena typedDict was passed
    if not isinstance(target, (Device, Application)):
        target = create_target(target)

    exclude_set = set(exclude or []).union({"BOT_ID", "UAVCAN_SCREEN_INITIAL_ANIMATION"})

    # Get existing variables
    existing_env_vars, existing_service_vars, service = target.get_variables()
    if delete_custom:
        custom_env_vars, custom_service_vars, _ = target.get_variables(custom=True)

    def update_variable(var_name, value, existing_vars, is_service_var=False):
        if existing_vars.get(var_name) != value and var_name not in exclude_set:
            if is_service_var and service:
                target.set_service_var(service, var_name, value)
            else:
                target.set_env_var(var_name, value)
            print(f"{var_name} set to {value} for {target.get_identifier()}")
        existing_vars.pop(var_name, None)

    # Turn off nodes not present in source when cloning
    if turn_off_nodes:

        def turn_off_variable(existing_vars, source_vars, is_service_var=False):
            for var_name in list(existing_vars):
                if var_name.startswith("NODE") and var_name not in exclude_set and source_vars.get(var_name) is None:
                    if existing_vars.get(var_name) != "0":
                        if is_service_var and service:
                            target.set_service_var(service, var_name, "0")
                        else:
                            target.set_env_var(var_name, "0")
                        print(f"{var_name} set to 0 for {target.get_identifier()}")
                    existing_vars.pop(var_name)

        turn_off_variable(existing_env_vars, source_env_vars)
        turn_off_variable(existing_service_vars, source_service_vars, True)

    # Update environment variables
    for var_name, value in source_env_vars.items():
        update_variable(var_name, value, existing_env_vars)

    # Update service variables
    for var_name, value in source_service_vars.items():
        update_variable(var_name, value, existing_service_vars, True)

    # Remove remaining custom variables (only for clone)
    if delete_custom:

        def remove_custom_variable(existing_vars, custom_vars, source_vars, is_service_var=False):
            for var_name in list(existing_vars):
                if (
                    var_name not in exclude_set
                    and var_name in custom_vars
                    and source_vars.get(var_name) != custom_vars.get(var_name)
                ):
                    if is_service_var and service:
                        target.remove_service_var(service, var_name)
                    else:
                        target.remove_env_var(var_name)
                    print(f"{var_name} removed for {target.get_identifier()}")
                    existing_vars.pop(var_name)

        remove_custom_variable(existing_env_vars, custom_env_vars, source_env_vars)  # type: ignore
        remove_custom_variable(existing_service_vars, custom_service_vars, source_service_vars, True)  # type: ignore


def change(variables: dict | str, targets: List[str]):
    if not targets:
        click.echo("Error: At least one target must be specified")
        return
    if isinstance(variables, str):
        env_vars, service_vars = {}, {}
        for var in variables.split(" "):
            if not VARIABLES_REGEX.match(var):
                raise ValueError("Variable must be in the format 'variable1=value=service' or 'variable1=value'")
            variable = var.split("=")

            if len(variable) <= 2 or variable[2] == "*":
                env_vars.update({variable[0]: variable[1]})
            else:
                service_vars.update({variable[0]: variable[1]})
    elif isinstance(variables, dict):
        env_vars, service_vars = variables["env_vars"], variables["service_vars"]["main"]
    else:
        click.echo("Error: Check 'variables' object class")
        return

    for target_id in targets:
        if BOT_ID_REGEX.match(target_id):
            target = get_device_by_id(target_id)
        else:
            target = get_fleet(target_id)

        if target:
            print(f"\nUpdating: {target_id}")
            update_variables(target, env_vars, service_vars)
            print(f"Successfully updated: {target_id}")


def clone(source: str, targets: tuple, exclude: str | None = None):
    if not targets:
        click.echo("At least one target device must be specified", err=True)
        return

    exclude_vars = set()
    if exclude is not None:
        for variable2exclude in exclude.split(" "):
            exclude_vars.add(variable2exclude)

    # Check if source is a device ID (4X000) or fleet
    if BOT_ID_REGEX.match(source):
        # Source is a device
        source_device = get_device_by_id(source)
        if not source_device:
            raise ValueError(f"Source device {source} not found")
        source_env_vars, source_service_vars, _ = get_device_variables(source_device)
    else:
        # Source is a fleet
        source_fleet = get_fleet(source)
        if not source_fleet:
            raise ValueError(f"Source fleet {source} not found")
        source_env_vars, source_service_vars, _ = get_fleet_variables(source_fleet)

    for target_id in targets:
        if not BOT_ID_REGEX.match(target_id):
            print(f"\033[93mFleet {target_id} selected as target!\033[0m")
            if not click.confirm("Are you sure you want to proceed?"):
                continue
            target = get_fleet(target_id)
        else:
            target = get_device_by_id(target_id)
        if target:
            print(f"\nUpdating: {target_id}")
            update_variables(
                target,
                source_env_vars,
                source_service_vars,
                exclude=exclude_vars,
                delete_custom=True,
                turn_off_nodes=True,
            )
            print(f"Successfully updated: {target_id}")


def purge(targets: List[str], exclude: str | None = None):
    exclude_vars = set()
    if exclude is not None:
        for variable2exclude in exclude.split(" "):
            exclude_vars.add(variable2exclude)

    for target_id in targets:
        if not BOT_ID_REGEX.match(target_id):
            print(f"Skipping invalid target ID format: {target_id}")
            continue
        target_device = get_device_by_id(target_id)
        if target_device:
            print(f"\nPurging device: {target_id}")
            env_vars, service_vars, service = get_device_variables(target_device, custom=True)
            delete_variables(target_device, env_vars, service_vars, service, exclude=exclude_vars)
            print(f"Successfully purged device: {target_id}")


def get(
    target: str | balena.types.models.TypeDevice, variable_name: str = "", custom: bool = False, all_vars: bool = False
) -> dict | str | None:
    target_device = get_device_by_id(target) if isinstance(target, str) else target

    if target_device:
        device_id = target_device["id"]

        if all_vars or custom:
            env_vars, service_vars, service = get_device_variables(target_device, custom=custom)
            result = {"env_vars": env_vars, "service_vars": {service: service_vars}}
            return result
        else:
            app_id = int(target_device["belongs_to__application"]["__id"])  # type: ignore
            service = get_service_id(target_device, "main")
            # Get device-specific variables
            value = balena_sdk.models.device.env_var.get(device_id, variable_name)
            if value is None:
                value = balena_sdk.models.device.service_var.get(device_id, service, variable_name)

            # Get fleet-level variables
            if value is None:
                value = balena_sdk.models.application.env_var.get(app_id, variable_name)
            if value is None:
                value = balena_sdk.models.service.var.get(service, variable_name)

            return value


def delete(variables: dict | str, targets: List[str]):
    if not targets:
        click.echo("Error: At least one target device must be specified")
        return
    if isinstance(variables, str):
        env_vars, service_vars = {}, {}
        for var in variables.split(" "):
            if not VARIABLES_REGEX.match(var):
                raise ValueError("Variable must be in the format 'variable1=value=service'")
            variable = var.split("=")

            if len(variable) <= 2 or variable[2] == "*":
                env_vars.update({variable[0]: variable[1]})
            else:
                service_vars.update({variable[0]: variable[1]})
    elif isinstance(variables, dict):
        env_vars, service_vars = variables["env_vars"], variables["service_vars"]["main"]
    else:
        click.echo("Error: Check 'variables' object class")
        return

    for target_id in targets:
        if not BOT_ID_REGEX.match(target_id):
            print(f"Skipping invalid target ID format: {target_id}")
            continue

        target_device = get_device_by_id(target_id)
        if target_device:
            service = get_service_id(target_device, "main")
            print(f"\nUpdating device: {target_id}")
            delete_variables(target_device, env_vars, service_vars, service)
            print(f"Successfully updated device: {target_id}")


def move(fleet, targets, keep_vars, keep_service_vars, clone, semver=None):
    if not targets:
        click.echo("At least one target device must be specified", err=True)
        return

    if BOT_ID_REGEX.match(fleet):
        click.echo(f"Error moving {', '.join(targets)} to {fleet}")
        return

    for target_id in targets:
        if not BOT_ID_REGEX.match(target_id):
            print(f"Skipping invalid target ID format: {target_id}")
            continue

        target_device = get_device_by_id(target_id)
        if not target_device:
            print(f"No target with ID found: {target_id}")
            continue

        print(f"\nMoving device: {target_id}")
        variables = {}
        if clone:
            variables = get(target_device, all_vars=True)
        elif keep_service_vars:
            variables = get(target_device, custom=True)

        balena_sdk.models.device.move(target_device["id"], ORGANIZATION_HANDLE + fleet)
        print(f"Successfully moved device {target_id} to {fleet}")

        release = find_release(fleet, semver)
        balena_sdk.models.device.pin_to_release(target_device["id"], release["id"])
        print(
            f"Pinned to release: {release['semver']}+rev{release['revision']}"
            if release["semver"] == "0.0.0"
            else f"Pinned to release: {release['semver']}"
        )

        if keep_service_vars or clone:
            target_device = get_device_by_id(target_id)
            service = next(iter(variables.get("service_vars", {})), None)  # type: ignore
            if clone:
                update_variables(target_device, variables["env_vars"], variables["service_vars"][service], turn_off_nodes=True)  # type: ignore
            else:
                update_variables(target_device, {}, variables["service_vars"][service])  # type: ignore
        elif not keep_vars:
            purge([target_id])


def schedule(json_file, date, date_format, tz, variables, targets) -> dict | None:
    # Helper function to process JSON file or command-line variables/targets
    def process_input_data(json_file, variables_str, targets):
        if json_file:
            printlog(f"Using JSON file: {json_file}", "INFO")
            dictionary: dict[str, dict | str] = convert_values_to_strings(load_json(json_file))  # type: ignore
            return dictionary
        elif variables_str and targets:
            return parse_targets_variables(targets, variables_str)
        else:
            printlog(
                "Both variables and targets are required when no JSON file is provided.",
                "ERROR",
            )
            ctx = click.get_current_context()
            ctx.exit(1)

    # Process input data (from JSON file or command-line arguments)
    message_data = process_input_data(json_file, variables, targets)

    task_id = uuid.uuid1()
    message_data["task_id"] = str(task_id)
    service_account = load_json(SERVICE_ACCOUNT)
    pubsub_message = format_pubsub_message(message_data)
    date_object = format_time(date, date_format, tz)
    confirmation = ask_confirmation(message_data, date_object, tz)  # type: ignore

    if confirmation.lower() in ["no", "n"]:
        printlog("Operation Aborted")
    elif confirmation.lower() in ["yes", "y"]:
        # Create the Cloud Task
        create_http_task(
            project=PROJECT_ID,
            location=LOCATION_ID,
            queue=QUEUE_ID,
            url=f"https://pubsub.googleapis.com/v1/projects/{PROJECT_ID}/topics/{PUBSUB_TOPIC}:publish",
            json_payload=pubsub_message,
            scheduled_datetime=date_object,
            task_id=task_id,
            service_account_client_email=service_account["client_email"],
        )
        printlog("Task created successfully", "OK_GREEN")

        # Add record to Google Sheets
        try:
            sheet = open_sheet(SERVICE_ACCOUNT, SPREADSHEET_NAME, "VarChangeLog")
            sheet.append_row(
                [
                    str(task_id),
                    datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    date_object.strftime("%Y-%m-%d %H:%M:%S GMT%Z"),
                    "",
                    False,
                    ", ".join([target for target in message_data["targets"]]),
                    ", ".join([f"{variable}={value}" for variable, value in message_data["variables"]["env_vars"].items()])  # type: ignore
                    + ", ".join(
                        [
                            f"{variable}={value}"
                            for variable, value in message_data["variables"]["service_vars"]["main"].items()  # type: ignore
                        ]
                    ),
                ]
            )
        except Exception as e:
            printlog(str(e), "ERROR")
            printlog(
                f"Error adding record to {SPREADSHEET_NAME}, task was still created",
                "WARN",
            )


def initialize(device, fleet):
    bots = balena_sdk.models.device.get_all_by_application(ORGANIZATION_HANDLE + "Production4_x")
    sorted_bots = sorted(bots, key=lambda d: d["created_at"], reverse=True)
    new_bot = sorted_bots[0]
    del bots, sorted_bots
    bot_to_delete = get_device_by_id(device)

    if bot_to_delete and click.confirm(
        f'Do you want to delete the old device {bot_to_delete.get("device_name")} and initialize {new_bot.get("device_name")}? ',
        default=True,
    ):
        bot_to_delete_uuid, new_bot_uuid = bot_to_delete.get("uuid"), new_bot.get("uuid")

        # Clone tags
        tags = balena_sdk.models.device.tags.get_all_by_device(bot_to_delete_uuid)
        tags = {tag["tag_key"]: tag["value"] for tag in tags}
        for key, value in tags.items():
            balena_sdk.models.device.tags.set(new_bot_uuid, key, value)

        # Delete old device
        balena_sdk.models.device.remove(bot_to_delete_uuid)
        balena_sdk.models.device.rename(new_bot.get("uuid"), bot_to_delete.get("device_name"))

        # Set bot_id var
        balena_sdk.models.device.env_var.set(
            new_bot_uuid, "BOT_ID", bot_to_delete.get("device_name").replace("kiwibot", "")
        )

        # Delete default config variables
        config_vars = balena_sdk.models.device.config_var.get_all_by_device(new_bot_uuid)
        config_vars = {config_var["name"]: config_var["value"] for config_var in config_vars}
        for name in config_vars:
            balena_sdk.models.device.config_var.remove(new_bot_uuid, name)

        move(
            fleet=fleet,
            targets=[bot_to_delete.get("device_name").removeprefix("kiwibot")],
            keep_vars=False,
            keep_service_vars=False,
            clone=False,
        )
        print(f"Device {bot_to_delete.get('device_name')} successfully initialized")


def rename(bot_id: str, new_id: str, version: str | None = None):
    # Validate input formats
    if not BOT_ID_REGEX.match(bot_id):
        print(f"ERROR: invalid target ID format: {bot_id}")
        exit(1)
    if not BOT_ID_REGEX.match(new_id):
        print(f"ERROR: invalid new ID format: {new_id}")
        exit(1)

    # Check bot existence
    bot_to_rename = get_device_by_id(bot_id)
    if not bot_to_rename:
        exit(1)
    if get_device_by_id(new_id) is not None:
        print(f"ERROR: Bot with id {new_id} already exists")
        exit(1)

    if click.confirm(
        f"Do you want to rename the device {bot_id} to {new_id}?",
        default=True,
    ):
        # Get bot UUID and tags
        bot_uuid = bot_to_rename.get("uuid")
        tags = {tag["tag_key"]: tag["value"] for tag in balena_sdk.models.device.tags.get_all_by_device(bot_uuid)}
        new_tags = ""
        exclude = ["City", "ROUTER_URL", "Team"]
        # Update tags if version is provided
        if version is not None:
            tags_file = load_json(TAGS_BY_VERSION_FILE)
            tags_file[version]
            # Remove all tags except "City"
            for key in list(tags.keys()):
                if key not in exclude:
                    balena_sdk.models.device.tags.remove(bot_uuid, key)
            # Set new tags from version file
            for key, value in tags_file[version].items():
                balena_sdk.models.device.tags.set(bot_uuid, key, value)
            new_tags = {
                tag["tag_key"]: tag["value"] for tag in balena_sdk.models.device.tags.get_all_by_device(bot_uuid)
            }

        # Rename the device and update BOT_ID
        balena_sdk.models.device.rename(bot_uuid, "kiwibot" + new_id)
        balena_sdk.models.device.env_var.set(bot_uuid, "BOT_ID", new_id)

        # Log the change
        try:
            sheet = open_sheet(SERVICE_ACCOUNT, SPREADSHEET_NAME, "ID change log")
            sheet.append_row(
                [
                    str(bot_id),
                    str(new_id),
                    os.uname().nodename,
                    datetime.datetime.now(datetime.timezone.utc).strftime("%Y/%m/%d %H:%M:%S"),
                    str(tags),
                    str(new_tags),
                    bot_uuid,
                ]
            )
        except Exception as e:
            printlog(str(e), "ERROR")
            printlog(
                f"Error adding record to {SPREADSHEET_NAME}, rename still occurred",
                "WARN",
            )

        print(f"Device {bot_id} successfully renamed to {new_id}")
