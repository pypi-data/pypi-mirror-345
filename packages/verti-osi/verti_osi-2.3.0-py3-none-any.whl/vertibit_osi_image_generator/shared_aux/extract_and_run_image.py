from vertibit_osi_image_generator.shared_aux.comand_runner import run_and_log_commands


def run_docker_image(image_name, ports={8000: 8000}):
    """
    Extracts a .tar file, loads a Docker image, and runs it, publishing specified ports.

    Args:
        ports (dict): A dictionary of ports to publish, e.g., {80: 8080} (host:container).
    Returns:
        str: The result of the Docker run command or an error message.
    """
    try:
        # Step 3: Build the Docker run command
        port_mappings = ""
        if ports:
            port_mappings = " ".join(
                [f"-p {host}:{container}" for host, container in ports.items()])

        run_cmd = f"docker run -it {port_mappings} {image_name}"

        run_and_log_commands(run_cmd)

    except Exception as e:
        return f"An unexpected error occurred: {e}"
