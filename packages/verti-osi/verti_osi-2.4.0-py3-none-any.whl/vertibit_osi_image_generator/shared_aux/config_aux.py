from typing import List, Dict, Any


def add_env_vars(env_list: List[str], env_type: str) -> List[Dict[str, str]]:
    """
    Converts a list of environment variables in the format "KEY=VALUE" into a list of dictionaries
    with the schema's required format: {"name": "KEY", "value": "VALUE", "type": "runtime/buildtime/both"}.
    """
    env_vars_formatted = []
    for env in env_list:
        if '=' in env:
            key, value = env.split('=', 1)
            env_vars_formatted.append({
                "name": key,
                "value": value,
                "type": env_type
            })
    return env_vars_formatted


def format_image_params_to_schema(
    platforms: str = "",
    repository_branch: str = "",
    repository_url: str = "",
    env_vars: List[str] = [],
    env_vars_rt: List[str] = [],
    env_vars_bt: List[str] = [],
    build_commands: List[str] = [],
    pre_build_commands: List[str] = [],
    root_directory: str = './',
    source_directory: str = './',
    image_name: str = "",
    daemon: str = 'docker',
    output: str = "",
    delete_generated_dockerfile: bool = False,
    port: int = 8080,
) -> Dict[str, Any]:

    # Initialize the schema dictionary
    schema_dict: Dict[str, Any] = {
        "image-name": image_name,
        "source-directory": source_directory,
        "root-directory": root_directory,
        "delete-generated-dockerfile": delete_generated_dockerfile,
        "daemon": daemon,
        "output-type": output if output else "normal",
        # Default platforms
        "platform": platforms.split(',') if platforms else ["linux/amd64", "linux/arm64"],
        # Empty array if none provided
        "pre-build": pre_build_commands if pre_build_commands else [],
        "build": build_commands if build_commands else [],  # Empty array if none provided
        "env-vars": [],  # Will be populated below
        "port": str(port),
    }

    # Add remote-source-repository if repository_url is provided
    if repository_url:
        schema_dict["remote-source-repository"] = {
            "git": {
                "url": repository_url,
                "branch": repository_branch if repository_branch else "main"
            }
        }

    # Add environment variables
    schema_dict["env-vars"].extend(add_env_vars(env_vars, "both"))
    schema_dict["env-vars"].extend(add_env_vars(env_vars_rt, "runtime"))
    schema_dict["env-vars"].extend(add_env_vars(env_vars_bt, "buildtime"))

    return schema_dict


def format_dockerfile_params_to_schema(
    repository_branch: str = "",
    repository_url: str = "",
    env_vars: List[str] = [],
    env_vars_rt: List[str] = [],
    env_vars_bt: List[str] = [],
    build_commands: List[str] = [],
    pre_build_commands: List[str] = [],
    root_directory: str = './',
    source_directory: str = './',
    port: int = 8080,
) -> Dict[str, Any]:

    # Initialize the schema dictionary
    schema_dict: Dict[str, Any] = {
        "source-directory": source_directory,
        "root-directory": root_directory,
        # Empty array if none provided
        "pre-build": pre_build_commands if pre_build_commands else [],
        "build": build_commands if build_commands else [],  # Empty array if none provided
        "env-vars": [],  # Will be populated below
        "port": str(port),
    }

    # Add remote-source-repository if repository_url is provided
    if repository_url:
        schema_dict["remote-source-repository"] = {
            "git": {
                "url": repository_url,
                "branch": repository_branch if repository_branch else "main"
            }
        }

    # Add environment variables
    schema_dict["env-vars"].extend(add_env_vars(env_vars, "both"))
    schema_dict["env-vars"].extend(add_env_vars(env_vars_rt, "runtime"))
    schema_dict["env-vars"].extend(add_env_vars(env_vars_bt, "buildtime"))

    return schema_dict
