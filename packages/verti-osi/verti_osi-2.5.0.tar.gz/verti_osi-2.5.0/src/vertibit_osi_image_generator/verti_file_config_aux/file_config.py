import os
import json
import yaml
from jsonschema import Draft7Validator
from importlib.resources import files


def load_config_schema(config_file='config.json'):
    """Load the JSON schema from a file within the package."""
    config_file = files("vertibit_osi_image_generator").joinpath(
        "config/config.json")
    if not config_file.is_file():
        raise FileNotFoundError(f"Config file not found at: {config_file}")
    with config_file.open("r") as file:
        return json.load(file)


def load_verti_config(config_path='verti-osi.yaml'):
    """
    Load and validate the configuration from the YAML file using the schema.

    Args:
        config_path (str): Path to the YAML configuration file.
        schema_path (str): Path to the JSON schema file.

    Returns:
        dict: The validated and processed configuration.
    """

    with open(config_path, "r") as file:
        config_dict = yaml.safe_load(file) or {}

    return config_dict


def apply_defaults(config, schema):
    """Recursively apply default values from schema to the config."""
    for key, value in schema.get("properties", {}).items():
        if key == "remote-source-repository" and key not in config:
            continue  # Skip applying defaults for remote-source-repository

        if key == "images" and key not in config:
            continue  # Skip applying defaults for remote-source-repository

        if key not in config and "default" in value:
            config[key] = value["default"]

        if isinstance(value.get("properties"), dict):  # If nested object, recurse
            config[key] = apply_defaults(config.get(key, {}), value)
    return config


def validate_config(config, schema):
    """
    Validate the config.

    Args:
        config (dict): The user-provided configuration.
        schema (dict): The JSON schema to validate against.

    Returns:
        dict: The validated configuration.
    """
    # Validate the config against the schema
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(config), key=lambda e: e.path)

    if errors:
        for error in errors:
            print(f"Validation error: {error.message}")
        raise ValueError(f"Validation error: {error.message}")

    return config


def verify_config_file(file_dir: str, verti_osi_config_file: str) -> bool:
    """
    Verify the existence of the verti_osi.yaml file in the provided directory.

    Args:
        file_dir (str): The directory to check for the verti_osi.yaml file.
        verti_osi_config_file (str): The name of the verti_osi.yaml file.

    Returns:
        bool: True if the file exists.

    Raises:
        FileNotFoundError: If the directory or config file does not exist.
    """
    if not file_dir:
        raise FileNotFoundError("Directory path is empty.")

    if not os.path.isdir(file_dir):
        raise FileNotFoundError(f"Directory does not exist: {file_dir}")

    verti_osi_config_path = os.path.join(file_dir, verti_osi_config_file)
    if not os.path.isfile(verti_osi_config_path):
        raise FileNotFoundError(
            f"Config file does not exist: {verti_osi_config_path}")

    return True
