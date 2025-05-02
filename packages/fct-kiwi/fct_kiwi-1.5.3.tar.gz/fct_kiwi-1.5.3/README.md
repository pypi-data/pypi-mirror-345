# FCT-Kiwi

A command-line tool for Balena device configuration management, allowing you to easily change, clone, purge, retrieve, and manage variables across devices and fleets.

## Table of Contents

- [FCT-Kiwi](#fct-kiwi)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Authentication](#authentication)
    - [Environment variables (Optional)](#environment-variables-optional)
  - [Commands](#commands)
    - [Usage in other scripts](#usage-in-other-scripts)
    - [Change](#change)
    - [Clone](#clone)
    - [Purge](#purge)
    - [Get](#get)
    - [Delete](#delete)
    - [Move](#move)
    - [Schedule](#schedule)
    - [Initialize](#initialize)
    - [Rename](#rename)
  - [File Format](#file-format)
    - [Changing variables](#changing-variables)
    - [Variable scheduling](#variable-scheduling)
    - [Tags by version](#tags-by-version)
  - [Error Handling](#error-handling)
  - [Dependencies](#dependencies)
  - [Author](#author)

## Installation

```bash
pip install fct-kiwi
```

## Authentication

To use this tool, you need to set up your Balena API key as an environment variable if you haven't already:

`export BALENA_API_KEY="your_api_key_here"`

An environment variables file can be defined as shown in the next section.

### Environment variables (Optional)

By default this is the order in which variables are read:

1. `.env` file
2. default
3. os.environ

Other variables might be needed for certain commands and are set by default, but can be overridden if necessary.

1. Create a `.env` file in the same directory as the script or set the path into your environment as `export FCT_ENV_PATH="/path/to/my/.env"`
2. Add your Balena API key: `BALENA_API_KEY=your_api_key_here`
3. Add other variables in new lines, this is a list of all variables used:
    - PROJECT_ID
    - SPREADSHEET_NAME
    - LOCATION_ID
    - QUEUE_ID
    - PUBSUB_TOPIC
    - AUTHOR
    - ORGANIZATION_HANDLE
    - GOOGLE_APPLICATION_CREDENTIALS
    - TAGS_BY_VERSION_FILE

## Commands

### Usage in other scripts

To use this packages functionality in other scripts simply import the functions you need from the following list.

```python
from fleet_control import clone, change, etc...
```

Otherwise you can use all commands from your terminal.

### Change

Change or create specified variable(s) to target device(s).

```bash
# Basic usage
fct change 'NODE_WEATHER_DEBUG=0=*' 4D163 4D164

# Change multiple variables
fct change 'NODE_WEATHER_DEBUG=0=* ANOTHER_VAR=value=service' 4D163 4D164

# Target a fleet
fct change 'NODE_WEATHER_DEBUG=0=*' Staging4_x

# Use a file containing variables
fct change --file variables.txt '' 4D163 4D164
```

### Clone

Clone configuration from a source device or fleet to target device(s).

```bash
# Clone from one device to others
fct clone 4E288 4D163 4D164

# Clone from a fleet to a device
fct clone Staging4_x 4D163

# Clone from a fleet to another fleet
fct clone Staging4_x fleet_name

# Clone with exclusions
fct clone --exclude "VAR1 VAR2" 4E288 4D163 4D164
```

### Purge

Purge all custom variables in target device(s).

```bash
# Purge all custom variables from devices
fct purge 4E288 4D163 4D164

# Purge with exclusions
fct purge --exclude "VAR1 VAR2" 4E288 4D163 4D164
```

### Get

Fetch variable value(s) for a device.

```bash
# Get a specific variable
fct get 4E288 UAVCAN_CHASSIS_CURRENT_T2

# Get all custom variables
fct get 4E288 --custom

# Get all variables (device + fleet)
fct get 4E288 --all-vars

# Save variables to a file
fct get 4E288 --output result.json
```

### Delete

Delete the overwritten value for specified variable(s) on the target device(s).

```bash
# Delete a variable
fct delete 'NODE_WEATHER_DEBUG=0=*' 4D163 4D164

# Delete multiple variables
fct delete 'VAR1=value=service VAR2=value=*' 4D163 4D164

# Delete variables from a file
fct delete --file variables.txt '' 4D163 4D164
```

### Move

Move target(s) from its current fleet to a specified fleet.

```bash
# Move devices to a new fleet
fct move Staging4_x 4E288 4D163 4D164

# Move keeping custom device variables
fct move --keep-vars Staging4_x 4E288 4D163 4D164

# Move keeping custom device and service variables
fct move --keep-service-vars Staging4_x 4E288 4D163 4D164

# Move with cloning (keep custom and previous fleet variables)
fct move --clone Staging4_x 4E288 4D163 4D164

# Move and pin to specific release
fct move --semver "1.3.11+rev87" Staging4_x 4E288 4D163 4D164
```

### Schedule

Schedule variable changes to be applied at a specific time. Service account file path required for creating the task. Set with the `GOOGLE_APPLICATION_CREDENTIALS` variable set in the `.env` file or in your environment.

```bash
# Schedule a change for tomorrow at 3 AM (default)
fct schedule 'WEATHER_NODE_DEBUG=0=main' 4B058 4D163

# Schedule with a specific date and time
fct schedule --date '2025-02-25 12:06:00' 'WEATHER_NODE_DEBUG=0=main' 4B058 4D163

# Schedule with a file containing variables
fct schedule --file vars.json --date '2025-02-25 12:06:00' '' 4B058

# Schedule with different timezone
fct schedule --tz 'America/New_York' 'WEATHER_NODE_DEBUG=0=main' 4B058 4D163
```

### Initialize

Initialize a target device with previous device tags, remove old device, delete default config variables, and move to specified fleet.

```bash
# Initialize a device and move it to a fleet
fct initialize Staging4_x 4E288
```

### Rename

Rename a target device with new ID. Optional new tags for corresponding version read from configuration file. Configuration file path set with the `TAGS_BY_VERSION_FILE` variable set in the `.env` file or in your environment.

```bash
# Rename a device
fct rename 4F407 4F265

# Rename a device and specify new version
fct rename --version "4.3F" 4F407 4F265
```

## File Format

### Changing variables

When using the `--file` option, the file should contain JSON formatted variables:

```json
{
  "env_vars": {
      "VAR1_NAME": "VAR1_VALUE",
      "VAR2_NAME": 2
  },
  "service_vars": {
      "main": {
        "SERVICE_VAR1_NAME": "SERVICE_VAR1_VALUE",
        "SERVICE_VAR2_NAME": "SERVICE_VAR2_VALUE"
      }
  }
}
```

### Variable scheduling

```json
{
  "targets": [
    "TARGET1_NAME",
    "TARGET2_NAME"
  ],
  "variables": {
    "env_vars": {
        "VAR1_NAME": "VAR1_VALUE",
        "VAR2_NAME": 2
    },
    "service_vars": {
        "main": {
          "SERVICE_VAR1_NAME": "SERVICE_VAR1_VALUE",
          "SERVICE_VAR2_NAME": "SERVICE_VAR2_VALUE"
        }
    }
  }
}
```

### Tags by version

```json
{
    "4.3B":{
        "Tag1": "value1",
        "Tag2": "value2",
    }
}
```

## Error Handling

The tool will return appropriate error messages if:

- The Balena API key is not set
- No variables are provided when required
- Target devices or fleets cannot be found
- API requests fail

## Dependencies

- balena-sdk
- click
- python-dotenv

## Author

Juan Pablo Castillo - <juan.castillo@kiwibot.com>
