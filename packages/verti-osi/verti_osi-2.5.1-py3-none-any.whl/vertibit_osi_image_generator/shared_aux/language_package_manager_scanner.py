import os
from vertibit_osi_image_generator.shared_aux.file_scanner_shared import scan_directory
from vertibit_osi_image_generator.shared_aux.language_package_managers import get_language_package_managers


# Main function for scanning directory
def main_language_scanner(directory: str):
    package_manager_files = get_language_package_managers()
    for language_info in package_manager_files:
        package_manager_file = language_info["package_manager_file"]['file_name']
        package_manager_extension = language_info["package_manager_file"]['extension']
        matching_file = scan_directory(
            directory, (package_manager_file, package_manager_extension))
        if matching_file != None:
            language_info['package_dir_path'] = matching_file
            return language_info
        else:
            print("%s package manager not found" % (language_info["language"]))
