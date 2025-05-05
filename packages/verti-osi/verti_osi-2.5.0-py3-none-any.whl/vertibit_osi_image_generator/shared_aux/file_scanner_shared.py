import os
import json
from typing import Dict, Any, Tuple, Union, List


def scan_for_json_key_value(data: Dict[Any, Any], path: Union[str, List[str]], separator: str = '.') -> Any:
    """
    Retrieves a value from a nested dictionary using a path-like string or list of keys.

    Parameters:
        data (Dict[Any, Any]): The dictionary to search through
        path (Union[str, List[str]]): Path to the desired value. Can be either:
            - A string with keys separated by separator (e.g., "key1.key2.key3")
            - A list of keys (e.g., ["key1", "key2", "key3"])
        separator (str): The separator to use when path is a string (default: '.')

    Returns:
        Any: The value found at the specified path

    Raises:
        KeyError: If the path cannot be found in the dictionary
        ValueError: If the path is empty or invalid
        TypeError: If the data is not a dictionary
    """
    if not isinstance(data, dict):
        raise TypeError("Input data must be a dictionary")

    if not path:
        raise ValueError("Path cannot be empty")

    # Convert string path to list of keys
    keys = path.split(separator) if isinstance(path, str) else path

    current = data
    for key in keys:
        current = current[key]
        if current:
            print(f"Key : {key}, identified")
            return current
        else:
            print(f"Key : {key}, not found")
            pass
    return {}


def scan_directory(directory: str, file_spec: Tuple[str, str]) -> str | None:
    """
    Scans a provided directory for a file matching specific filename and extension.
    Only checks the provided directory, not subdirectories.

    Parameters:
        directory (str): The directory to scan.
        file_spec (Tuple[str, str]): Tuple containing (filename, extension) pair
                                    Example: ('package', 'json')
                                    Note: Extension should not include the dot.

    Returns:
        str | None: Full path of the matching file if found, None otherwise.

    Raises:
        ValueError: If the provided directory is invalid or file_spec format is incorrect.
    """
    if not os.path.isdir(directory):
        raise ValueError(
            f"The provided path is not a valid directory: {directory}")

    # Validate file_spec format
    filename, extension = file_spec
    if not isinstance(filename, str) or not isinstance(extension, str):
        raise ValueError(
            "file_spec must be a tuple of (filename, extension) as strings")
    if not filename or not extension:
        raise ValueError(
            "Both filename and extension must be non-empty strings")
    if '.' in filename or '.' in extension:
        raise ValueError(
            "Filename and extension should be provided separately without dots")

    # List files in the directory (not recursive)
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        # Skip if not a file
        if not os.path.isfile(file_path):
            continue

        # Split the filename and extension
        name, ext = os.path.splitext(file)
        # Remove the dot from extension
        ext = ext[1:] if ext.startswith('.') else ext

        # Check if the file matches the specification
        if name.lower() == filename.lower() and ext.lower() == extension.lower():
            return file_path

    return None

def open_json_file(file_path: str) -> Dict[Any, Any]:
    """
    Reads a JSON file and returns its contents as a dictionary.

    Parameters:
        file_path (str): Path to the JSON file to read.

    Returns:
        Dict[Any, Any]: Dictionary containing the JSON file contents.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        PermissionError: If the program lacks permission to read the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} was not found")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON format in {
                                   file_path}: {str(e)}", e.doc, e.pos)
    except PermissionError:
        raise PermissionError(
            f"Permission denied when trying to read {file_path}")
    except Exception as e:
        raise Exception(f"An error occurred while reading {
                        file_path}: {str(e)}")


def read_text_file(file_path: str) -> str:
    """
    Reads a text file and returns its contents as a string.

    Parameters:
        file_path (str): Path to the text file to read.

    Returns:
        str: Contents of the text file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the program lacks permission to read the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} was not found")
    except PermissionError:
        raise PermissionError(
            f"Permission denied when trying to read {file_path}")
    except Exception as e:
        raise Exception(f"An error occurred while reading {
                        file_path}: {str(e)}")


def scan_txt_file_for_key(text: str, search_key: str) -> Tuple[str | None, bool]:
    """
    Scans a string for a specific search key and returns the complete word containing that key
    along with a boolean indicating if the key was found.

    Parameters:
        text (str): The text to search through
        search_key (str): The key to search for (case-insensitive)

    Returns:
        Tuple[str | None, bool]: A tuple containing:
            - The complete word containing the search key (or None if not found)
            - Boolean indicating if the search key was found

    Example:
        text = "Hello World package.json is here"
        word, found = find_word_with_key(text, "package")
        # Returns: ("package.json", True)
    """
    if not text or not search_key:
        return None, False

    # Convert to lowercase for case-insensitive search
    text_lower = text.lower()
    search_key_lower = search_key.lower()

    # Split text into words
    words = text.split()

    # Search for the key in each word
    for word in words:
        if search_key_lower in word.lower():
            return word, True

    return None, False


def find_matching_key(obj, keys_to_check):
    """
    Check if an object (dictionary) contains any of the specified keys.

    Args:
        obj (dict): The dictionary to check.
        keys_to_check (list): A list of keys to search for.

    Returns:
        str: The name of the first matching key, or None if no keys match.
    """
    for key in keys_to_check:
        if key in obj:
            return key
    return None

def scan_for_main_modules(main_modules_info, root_directory, source_directory):
    for file_name in main_modules_info['filenames']:
        file_exists_in_root_dir = scan_directory(
            root_directory, (file_name, main_modules_info['extension']))
        if file_exists_in_root_dir != None:
            return (file_name, True)

        file_exists_in_source_dir = scan_directory(
            source_directory, (file_name, main_modules_info['extension']))
        if file_exists_in_source_dir != None:
            return (file_name, True)

    return (None, False)

def clean_module_path(path: str) -> str:
    # Remove leading dots
    cleaned = path.lstrip('.')
    
    # Remove .py extension if it exists
    if cleaned.endswith('.py'):
        cleaned = cleaned[:-3]
        
    return cleaned