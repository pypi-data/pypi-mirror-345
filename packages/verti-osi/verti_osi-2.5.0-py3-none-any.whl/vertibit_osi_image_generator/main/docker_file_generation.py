from vertibit_osi_image_generator.nodejs.docker_file_generation import generate_nodejs_dockerfile
from vertibit_osi_image_generator.python.docker_file_generation import generate_python_dockerfile
from vertibit_osi_image_generator.nodejs.docker_file_generation_prep import prepeare_nodejs_docker_file_generation
from vertibit_osi_image_generator.python.docker_file_generation_prep import prepare_python_docker_file_generation


def main_docker_file_generator(language_info, images, source_directory, root_directory, env_vars, port):
    if language_info['language'] == 'NodeJs':
        nodejs_prep = prepeare_nodejs_docker_file_generation(
            root_directory=root_directory, source_directory=source_directory, language_info=language_info)
        package_directories = nodejs_prep['package_directories']
        installation_command = nodejs_prep['install_command']
        start_command = nodejs_prep['entry_point']
        return generate_nodejs_dockerfile(dev_base_image=images['build'], prod_base_image=images['run-time'], package_manager_dir=package_directories,
                                          entry_point=start_command, install_command=installation_command, source_dir=source_directory, environment_variables=env_vars, port=port)
    elif language_info['language'] == 'Python':
        python_prep = prepare_python_docker_file_generation(
            root_directory=root_directory, source_directory=source_directory, language_info=language_info)
        start_command = python_prep['entry_point']
        return generate_python_dockerfile(dev_base_image=images['build'], prod_base_image=images['run-time'], package_manager_dir=language_info['package_dir_path'],
                                          entry_point=start_command, source_dir=source_directory, environment_variables=env_vars, port=port)
    elif language_info['language'] == 'Maven':
        print("Maven dockerfile generation doesn't exist.")
        pass
    elif language_info['language'] == 'Gradle':
        print("Gradle dockerfile generation doesn't exist.")
        pass
