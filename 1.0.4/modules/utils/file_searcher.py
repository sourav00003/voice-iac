import os

def find_file_within_project(filename):
    """
    Recursively search for the given filename starting from the project root
    where main.py is located.
    """
    # Step 1: Start from current file's directory
    current_dir = os.path.abspath(os.path.dirname(__file__))

    # Step 2: Walk upwards until main.py is found (project root)
    while True:
        if "main.py" in os.listdir(current_dir):
            break
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            # Reached filesystem root
            return None
        current_dir = parent

    # Step 3: Walk downward from project root
    for root, dirs, files in os.walk(current_dir):
        if filename in files:
            return os.path.join(root, filename)

    return None
