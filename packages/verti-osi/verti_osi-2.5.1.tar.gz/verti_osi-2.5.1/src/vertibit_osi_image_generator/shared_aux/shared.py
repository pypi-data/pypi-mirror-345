import os
import random
import string
import shutil


def delete_files(file_paths):
    """
    Deletes multiple files at the specified file paths.

    Args:
        file_paths (list): A list of file paths to be deleted.

    Returns:
        dict: A dictionary with file paths as keys and results as values.
    """
    results = {}

    for file_path in file_paths:
        try:
            os.remove(file_path)
            results[file_path] = "Deleted successfully."
        except FileNotFoundError:
            results[file_path] = "File does not exist."
        except PermissionError:
            results[file_path] = "Permission denied."
        except Exception as e:
            results[file_path] = f"Error: {e}"

    for file, result in results.items():
        print(f"{file}: {result}")

    return results


def generate_random_string(length=4):
    return ''.join(random.choices(string.ascii_lowercase + string.digits + string.octdigits, k=length))

def format_directory(directory:str) -> str:
    """
    Format directory string according to specified rules:
    - Verifies input is a string
    - If directory is ".", convert to "./"
    - If directory is anything else, add "/" to produce "/directory"
    - If directory already follows the standard format, leave it unchanged
    
    Args:
        directory (str): Directory string to format
    
    Returns:
        str: Properly formatted directory string
        
    Raises:
        TypeError: If directory is not a string
    """
    # Check if input is a string
    if not isinstance(directory, str):
        raise TypeError("Directory must be a string")
    
    if not directory:
        return "/"
    
    # Case: directory is "."
    if directory == ".":
        return "./"
    
    # Case: directory already starts with "/"
    if directory.startswith("/"):
        return directory
    
    # Case: directory already ends with "/"
    if directory.endswith("/"):
        return "/" + directory
    
    # Default case: add "/" prefix to directory
    return "/" + directory


def copy_file(source_path, destination_dir):
    """
    Copy a file from source_path to destination_dir.
    
    Args:
        source_path (str): Path to the source file
        destination_dir (str): Directory where the file will be copied to
    """
    # Check if source file exists
    if not os.path.isfile(source_path):
        print(f"Error: Source file '{source_path}' does not exist.")
        return False
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        print(f"Destination directory '{destination_dir}' does not exist. Creating it...")
        os.makedirs(destination_dir)
    
    # Get just the filename from the source path
    file_name = os.path.basename(source_path)
    
    # Create the full destination path
    destination_path = os.path.join(destination_dir, file_name)
    
    # Copy the file
    try:
        shutil.copy2(source_path, destination_path)
        print(f"Successfully copied '{source_path}' to '{destination_path}'")
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False