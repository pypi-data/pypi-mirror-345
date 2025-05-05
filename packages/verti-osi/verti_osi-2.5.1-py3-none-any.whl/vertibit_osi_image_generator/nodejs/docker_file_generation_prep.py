from vertibit_osi_image_generator.nodejs.nodejs_config import scan_for_js_package_manager_to_use, generate_nodejs_start_and_install_commands, generate_js_package_config_requirements

def prepeare_nodejs_docker_file_generation(root_directory, source_directory, language_info):
    package_manager_info = scan_for_js_package_manager_to_use(
        root_directory, language_info)
    start_and_installation_command = generate_nodejs_start_and_install_commands(
        root_directory, source_directory, language_info)
    package_directories = generate_js_package_config_requirements(
        package_manager_info, language_info['package_dir_path'])
    return {'package_directories': package_directories, 'entry_point': start_and_installation_command['start_command'], 'install_command': start_and_installation_command['installation_command'], 'source_dir': source_directory}