from vertibit_osi_image_generator.shared_aux.shared import format_directory


def generate_nodejs_dockerfile(
    dev_base_image: str,
    prod_base_image: str,
    package_manager_dir: str = None,
    entry_point: list = None,
    base_dir: str = "/base",
    runtime_dir: str = "/app",
    install_command: str = "npm install",
    source_dir: str = "src",
    environment_variables: list = [],
    group_id: int = 1001,
    user_id: int = 1001,
    port: int = 8000
) -> str:
    """
    Generates a Dockerfile as a string based on the provided parameters.

    Parameters:
        base_image (str): The base image for the Dockerfile (e.g., "python:3.9-slim").
        working_dir (str): The working directory inside the container (default: "/app").
        environment_vars (dict): A dictionary of environment variables (default: None).
        install_commands (list): A list of shell commands to install dependencies (default: None).
        copy_commands (list): A list of (source, destination) tuples for files to copy (default: None).
        entrypoint (list): A list of entrypoint commands (default: None).

    Returns:
        str: A string representation of the generated Dockerfile.
    """
    lines = []

    # Development stage
    lines.append(f"FROM {dev_base_image} AS build-time")
    lines.append(f"WORKDIR {base_dir}")

    # Set required env variables
    if len(environment_variables) > 0:
        for env_var in environment_variables:
            if env_var['type'] == "both" or env_var['type'] == "buildtime":
                lines.append(f"ENV {env_var['name']}={env_var['value']}")

    lines.append("ENV NODE_ENV=production")
    lines.append(f"COPY {package_manager_dir} {format_directory('.')}")
    lines.append(f"RUN {install_command}")

    # Section Spearator
    lines.append(f"####")

    # Final stage
    lines.append(f"FROM {prod_base_image} AS run-time")
    lines.append(f"WORKDIR {runtime_dir}")

    # Creating new user and group
    group_name = "nodeappgroup"
    user_name = "nodeappuser"

    lines.append(f"ARG UID={user_id}")
    lines.append(f"ARG GID={group_id}")

    lines.append(f"RUN addgroup --gid $GID {group_name} && adduser --uid $UID --ingroup {
                 group_name} --system {user_name}")

    if len(environment_variables) > 0:
        # Set required env variables
        for env_var in environment_variables:
            if env_var['type'] == "both" or env_var['type'] == "runtime":
                lines.append(f"ENV {env_var['name']}={env_var['value']}")

    lines.append(
        f"COPY --from=build-time {base_dir}/node_modules /node_modules")

    lines.append(
        f"COPY --chown={user_name}:{group_name} {package_manager_dir} {format_directory('.')}")
    lines.append(
        f"COPY --chown={user_name}:{group_name} {source_dir} {format_directory(source_dir)}")
    
    lines.append(f"RUN chown -R {user_name}:{group_name} {runtime_dir}")

    # Section Spearator
    lines.append(f"####")

    lines.append(f"ENV PORT={port}")

    lines.append(f"EXPOSE {port}")

    lines.append(f"USER {user_name}")

    # Section Spearator
    lines.append(f"####")

    # Entrypoint
    lines.append(f'ENTRYPOINT {entry_point}')

    return "\n".join(lines)
