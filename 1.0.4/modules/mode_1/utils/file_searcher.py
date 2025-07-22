import os

def find_file_within_project(filename: str, project_root: str) -> str | None:
    """
    Searches recursively for a file named `filename` starting from `project_root`.
    Returns the full path if found, otherwise returns None.
    """
    for root, _, files in os.walk(project_root):
        if filename in files:
            return os.path.join(root, filename)
    return None