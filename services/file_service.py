# services/file_service.py

import os
from typing import List

def find_robot_files(directory: str, include_subfolders: bool) -> List[str]:
    """
    Scans a directory for .robot files.

    Args:
        directory (str): The path to the directory to scan.
        include_subfolders (bool): Whether to scan subfolders recursively.

    Returns:
        List[str]: A list of full paths to the found .robot files.
    """
    robot_files = []
    if include_subfolders:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".robot"):
                    robot_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            if file.endswith(".robot") and os.path.isfile(os.path.join(directory, file)):
                robot_files.append(os.path.join(directory, file))
                
    return robot_files