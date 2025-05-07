from os import path

WINDOWS_PATH_SEP = "\\"
UNIX_PATH_SEP = "/"

def fix_path(file_path: str) -> str:
    """Replaces all path separators, be they Linux or Windows style
    to the standard path separator of the system.

    Args:
        file_path (str): The file path to fix.
    """
    for str in [ WINDOWS_PATH_SEP, UNIX_PATH_SEP ]:
        if str != path.sep:
            file_path = file_path.replace(str, path.sep)

    return file_path

def get_relative_path(file_path: str, root: str) -> str:
    """Get the path relative to root path.

    Args:
        file_path (str): The path.
        root (str): The root path.

    Returns:
        str: The relative path.
    """
    if root == file_path:
        return file_path
    else:
        return path.relpath(file_path, path.commonprefix([root, file_path]))