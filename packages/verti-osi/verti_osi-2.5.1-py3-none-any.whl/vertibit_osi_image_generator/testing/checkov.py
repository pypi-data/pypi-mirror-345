from vertibit_osi_image_generator.shared_aux.comand_runner import run_and_log_commands


def checkov_check(file_path):
    """
    Run Checkov on the specified directory.

    Args:
        directory (str): The directory to run Checkov on.
        checkov_path (str): The path to the Checkov executable.

    Returns:
        str: The output of the Checkov command.
    """
    framework = 'dockerfile'

    command = f"checkov --file {file_path} --framework {framework} --skip-check CKV_DOCKER_2"
    result = run_and_log_commands(command)
    return result
