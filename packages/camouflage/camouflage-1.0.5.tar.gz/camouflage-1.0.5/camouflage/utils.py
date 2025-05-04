import os


def extract_module_name(filepath: str) -> str:
    """Extract the module name from a given file path.

    Args:
        filepath (str): The file path to extract the module name from.

    Returns:
        str: The extracted module name.

    Raises:
        ValueError: If the module name is not a valid Python identifier.

    """
    module_name = os.path.basename(filepath).replace(".py", "")
    if not module_name.isidentifier():
        raise ValueError(
            f"Invalid filename [{module_name}]. Must be a valid Python identifier."
        )
    return module_name
