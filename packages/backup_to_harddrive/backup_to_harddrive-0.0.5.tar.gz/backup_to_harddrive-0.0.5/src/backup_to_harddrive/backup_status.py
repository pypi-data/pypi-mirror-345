"""Method to handle set and read backup status."""

import codecs
from pathlib import Path

from platformdirs import user_config_dir


def get_path_for_backup_status() -> Path:
    """Get the path to the file containing the backup status.

    Returns:
        Path: The path to the file containing the backup status.
    """
    return Path(user_config_dir("backup_to_harddrive")) / "backup_status.txt"


def is_backup_switched_on(filename=get_path_for_backup_status()) -> bool:
    """Get the backup status.

    Args:
        filename (str): The path to the file containing the backup status.
    Returns:
        bool: The backup status.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = [line.rstrip("\n") for line in file]
        return content[0] == "On"
    except FileNotFoundError:
        print("Backup status file not found")
        return True


def set_backup_status(on_or_off: bool) -> None:
    """Set the backup status.

    Args:
        on_or_off (bool): The backup status.
    """
    get_path_for_backup_status().parent.mkdir(parents=True, exist_ok=True)
    with codecs.open(str(get_path_for_backup_status().absolute()), "w+", encoding="utf_8") as file:
        if on_or_off:
            file.write("On")
        else:
            file.write("Off")
