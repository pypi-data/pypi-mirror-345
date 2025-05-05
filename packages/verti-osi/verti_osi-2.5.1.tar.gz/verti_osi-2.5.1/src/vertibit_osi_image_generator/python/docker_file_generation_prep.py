from vertibit_osi_image_generator.python.python_config import generate_python_start_command

def prepare_python_docker_file_generation(root_directory, source_directory, language_info):
    start_command = generate_python_start_command(
        root_directory, source_directory, language_info)
    return {'entry_point': start_command, 'source_dir': source_directory}