import os
from vertibit_osi_image_generator.shared_aux.file_scanner_shared import read_text_file, scan_txt_file_for_key, scan_directory, scan_for_main_modules, clean_module_path


def generate_python_start_command(root_directory, source_directory, language_info):
    start_comand = ''
    django_project, is_django_app = scan_for_django_app(
        language_info['package_dir_path'], root_directory)

    if is_django_app:
        start_comand = generate_django_start_command(django_project)
        return start_comand

    fast_api_main_module_path, is_fast_api_app = scan_for_fastapi_app(
        language_info['package_dir_path'], language_info['main_modules'], root_directory, source_directory)

    if is_fast_api_app:
        module_path = replace_slash_with_dot(fast_api_main_module_path)
        cleaned_module_path = clean_module_path(module_path)
        start_comand = generate_fastapi_start_command(cleaned_module_path)
        return start_comand

    flask_main_module_path, is_flask_app = scan_for_flask_app(
        language_info['package_dir_path'], language_info['main_modules'], root_directory, source_directory)

    if is_flask_app:
        module_path = replace_slash_with_dot(flask_main_module_path)
        cleaned_module_path = clean_module_path(module_path)
        start_comand = generate_flask_start_command(cleaned_module_path)
        return start_comand

    main_module_path, main_module_exists = scan_for_main_modules(
        main_modules_info=language_info['main_modules'], root_directory=root_directory, source_directory=source_directory)

    if main_module_exists:
        start_comand = generate_standard_python_start_command(main_module_path)
        return start_comand

    # Throw error if none


def find_django_directory(root_directory):
    # List of required files
    required_files = {"settings.py", "urls.py", "asgi.py", "wsgi.py"}

    # Walk through the directory tree
    for dirpath, _, filenames in os.walk(root_directory):
        # Check if the set of required files is a subset of the current directory's files
        if required_files.issubset(set(filenames)):
            # Return the name of the directory
            return os.path.basename(dirpath)

    return None  # Return None if no such directory is found


def scan_for_django_app(file_path: str, root_directory):
    text_file_content = read_text_file(file_path)
    _, package_exists = scan_txt_file_for_key(text_file_content, 'django')
    django_manage_file_exists = scan_directory(
        root_directory, ('manage', 'py'))

    django_directory = find_django_directory(root_directory)

    if package_exists and django_manage_file_exists != None and django_directory != None:
        return (django_directory, True)

    return (None, False)


def scan_for_fastapi_app(file_path: str, main_modules_info, root_directory, source_directory):
    text_file_content = read_text_file(file_path)
    _, package_exists = scan_txt_file_for_key(text_file_content, 'fastapi')

    if package_exists:
        for file_name in main_modules_info['filenames']:
            file_exists_in_root_dir = scan_directory(
                root_directory, (file_name, main_modules_info['extension']))
            if file_exists_in_root_dir != None:
                return (file_exists_in_root_dir, True)

            file_exists_in_source_dir = scan_directory(
                source_directory, (file_name, main_modules_info['extension']))
            if file_exists_in_source_dir != None:
                return (file_exists_in_source_dir, True)

    return (None, False)


def scan_for_flask_app(file_path: str, main_modules_info, root_directory, source_directory):
    text_file_content = read_text_file(file_path)
    _, package_exists = scan_txt_file_for_key(text_file_content, 'flask')

    if package_exists:
        for file_name in main_modules_info['filenames']:
            file_exists_in_root_dir = scan_directory(
                root_directory, (file_name, main_modules_info['extension']))
            if file_exists_in_root_dir != None:
                return (file_exists_in_root_dir, True)

            file_exists_in_source_dir = scan_directory(
                source_directory, (file_name, main_modules_info['extension']))
            if file_exists_in_source_dir != None:
                return (file_exists_in_source_dir, True)

    return (None, False)


def generate_flask_start_command(entry_file):
    start_command = f'["python","-m","gunicorn", "-w" ,"4", "-b", "0.0.0.0:8000", "{
        entry_file}:app"]'

    return start_command


def generate_fastapi_start_command(entry_file):
    start_command = f'["python","-m","uvicorn" ,"{
        entry_file}:app" ,"--host", "0.0.0.0", "--port", "8000", "--workers", "4"]'

    return start_command


def generate_django_start_command(project_dir):
    start_command = f'["python","-m","gunicorn", "-w" ,"4", "-b", "0.0.0.0:8000", "{
        project_dir}.wsgi:app"]'

    return start_command


def generate_standard_python_start_command(entry_file):
    start_command = f'["python","{entry_file}"]'

    return start_command


def replace_slash_with_dot(path):
    """
    Replaces all occurrences of '/' with '.' in the given path string.

    Parameters:
    path (str): The path string to be converted.

    Returns:
    str: The converted path with '.' instead of '/'.
    """
    return path.replace("/", ".")
