import os
import zipfile

def extract_zip(zip_file_path: str, extract_to: str) -> None:
    """
    Extracts a ZIP file to the specified directory.

    :param zip_file_path: Path to the ZIP file.
    :param extract_to: Directory where the contents will be extracted.
    """
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def list_code_files(directory: str) -> list:
    """
    Lists all code files based on supported extensions within a directory (recursively).

    :param directory: The root directory to search.
    :return: List of relative file paths for each code file.
    """
    supported_extensions = [
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cs',
        '.go', '.php', '.rb', '.rs', '.swift', '.kt', '.m', '.scala', '.sh',
        '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.sql', '.r', '.ipynb'
    ]
    code_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in supported_extensions):
                code_files.append(os.path.relpath(os.path.join(root, file), directory))
    return code_files

def read_file(file_path: str) -> str:
    """
    Reads and returns the content of a file.

    :param file_path: The path to the file.
    :return: The content of the file as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"
