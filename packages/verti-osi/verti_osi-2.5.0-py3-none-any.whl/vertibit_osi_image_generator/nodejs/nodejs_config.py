from vertibit_osi_image_generator.shared_aux.file_scanner_shared import scan_for_json_key_value, open_json_file, find_matching_key, scan_directory, scan_for_main_modules


def generate_nodejs_start_and_install_commands(root_directory, source_directory, language_info):
    start_command = ''
    package_manager_info = scan_for_js_package_manager_to_use(
        root_directory, language_info)
    installation_command = nodejs_installation_command(package_manager_info)
    start_script_key, start_script_key_exists = scan_nodejs_start_command(
        language_info['package_dir_path'], language_info)

    if start_script_key_exists:
        start_command = generate_nodejs_start_command(
            package_manager_info['package_manager'], start_script_key)
    else:
        main_module_path, main_module_path_exists = scan_for_main_modules(
            language_info['main_modules'], root_directory, source_directory)

        if main_module_path_exists:
            start_command = generate_standard_nodejs_start_command(
                main_module_path)
        else:
            # come back to throw error
            pass

    return {'start_command': start_command, 'installation_command': installation_command}


def scan_nodejs_start_command(file_path: str, language_info):
    scripts_object = retrieve_nodejs_scripts(file_path)

    start_key = find_matching_key(
        scripts_object, language_info['start_scripts'])

    if start_key != None:
        return (start_key, True)

    return (None, False)


def scan_nodejs_version(file_path: str):
    json_content = open_json_file(file_path)
    node_version = scan_for_json_key_value(json_content, path="engines.node")

    if node_version != None:
        return (node_version, True)

    return (None, False)


def retrieve_nodejs_scripts(file_path: str):
    json_content = open_json_file(file_path)
    scripts_object = scan_for_json_key_value(json_content, path="scripts")

    if scripts_object:
        return scripts_object

    return {}


def generate_nodejs_start_command(package_manager, start_command):
    if package_manager == 'yarn':
        return f'["{package_manager}", "{start_command}"]'

    if package_manager == 'npm':
        return f'["{package_manager}", "run", "{start_command}"]'


def generate_standard_nodejs_start_command(entry_file):
    return f'["node", "{entry_file}"]'


def scan_for_js_package_manager_to_use(root_directory, language_info):
    for lock_file in language_info['lock_files']:
        file_name = lock_file['filename']
        file_path = scan_directory(
            root_directory, (lock_file['filename'], lock_file['extension']))
        if file_path != None:
            print(f"lock file identified: {file_name}")
            print(f"package manager to be used: {
                  lock_file['package_manager']}")
            return {'package_manager': lock_file['package_manager'], 'locked': True, 'lock_file_path': file_path}

    return {'package_manager': "npm", 'locked': False}


def nodejs_installation_command(package_info):
    if package_info['package_manager'] == 'npm':
        if package_info['locked']:
            return f'npm ci'
        else:
            return f'npm install'
    elif package_info['package_manager'] == 'yarn':
        if package_info['locked']:
            return f'yarn install --frozen-lockfile'
        else:
            return f'yarn install'


def generate_js_package_config_requirements(package_info, package_manager_dir):
    if package_info['locked']:
        return f"{package_manager_dir} {package_info['lock_file_path']}"
    else:
        return package_manager_dir
