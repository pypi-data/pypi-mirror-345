import platform

def is_system_compatible(system_config) -> bool:
    """
    Check if the current system is compatible with the given system config.

    Args:
        system_config (str or list[str]): The 'system' field from YAML.

    Returns:
        bool: True if the current system matches the config, False otherwise.
    """
    if not system_config:
        return False  # defensive default

    # Normalize current platform
    current_system = platform.system().lower()  # e.g., "linux", "darwin", "windows"
    if current_system == "darwin":
        current_system = "macos"

    # Normalize config
    if isinstance(system_config, str):
        system_config = [system_config]

    normalized_config = {s.strip().lower() for s in system_config}

    return "all" in normalized_config or current_system in normalized_config
