"""Functions to handle reading from config files."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml
import yaml.scanner
from platformdirs import user_config_dir


@dataclass
class BackupConfig:
    """Configuration of a single backup use case."""

    source: Path
    list_of_harddrive: List[Path]
    list_of_excluded_folders: List[Path]
    quick_restore_path: List[Path]


@dataclass
class RunConfig:
    """Dataclass to hold configuration values for the whole run."""

    backup_configs: List[BackupConfig]


def get_path_to_config_file_and_initialize_if_none() -> Path:
    """Get the path to the configuration file.

    If the file does not exists, it will create an empty one, including parent directory if necessary

    Returns:
        Path: The path to the configuration file.
    """
    config_dir = Path(user_config_dir("backup_to_harddrive"))
    config_file_path = config_dir / "config.yaml"
    if not config_dir.exists():
        config_file_path.parent.mkdir(parents=True, exist_ok=True)
        config_file_path.touch(mode=0o600, exist_ok=True)
    return config_file_path


def is_populating_config_with_valid_source_successful(
    config_dict: dict, backup: str, backup_config: BackupConfig
) -> bool:
    """Populate the backup configuration with valid source.

    Args:
        config_dict (dict): Dictionary containing the configuration data (read from a YAML file for example).
        backup (str): Key to look for in the dictionary.
        backup_config (BackupConfig): Backup configuration to populate.
    Returns:
        bool: True if source is valid, False otherwise.
    """
    try:
        backup_config.source = Path(config_dict["backup_configurations"][backup]["source"])
    except KeyError as error:
        logging.error("Missing key for backup configuration: %s Configuration skipped.\n%s", backup, error)
        return False
    if not backup_config.source.exists():
        logging.error(
            "Source folder: %s does not exist for configuration: %s Configuration skipped.",
            str(backup_config.source),
            backup,
        )
        return False
    return True


def is_populating_config_with_at_least_one_valid_list_of_harddrive_successful(
    config_dict: dict, backup: str, backup_config: BackupConfig
) -> bool:
    """Populate the backup configuration with valid harddrive paths.

    Args:
        config_dict (dict): Dictionary containing the configuration data (read from a YAML file for example).
        backup (str): Key to look for in the dictionary.
        backup_config (BackupConfig): Backup configuration to populate.
    Returns:
        bool: True if at least one harddrive is valid, False otherwise.
    """
    try:
        listed_harddrive = [
            Path(harddrive) for harddrive in config_dict["backup_configurations"][backup]["list_of_harddrive"]
        ]
    except KeyError as error:
        logging.error("Missing key for backup configuration: %s Configuration skipped.\n%s", backup, error)
        return False
    for harddrive in listed_harddrive:
        if not harddrive.exists():
            logging.error(
                "Harddrive: %s does not exist for configuration: %s Harddrive skipped.", str(harddrive), backup
            )
        else:
            backup_config.list_of_harddrive.append(harddrive)
    if not backup_config.list_of_harddrive:
        logging.error("No harddrive available for configuration: %s. Configuration skipped.", backup)
        return False
    return True


def populate_config_with_valid_excluded_folders(config_dict: dict, backup: str, backup_config: BackupConfig) -> None:
    """Populate the backup configuration with valid excluded folders.

    Args:
        config_dict (dict): Dictionary containing the configuration data (read from a YAML file for example).
        backup (str): Key to look for in the dictionary.
        backup_config (BackupConfig): Backup configuration to populate.
    """
    try:
        listed_excluded_folders = config_dict["backup_configurations"][backup]["list_of_excluded_folders"]
        if listed_excluded_folders is None:
            logging.warning(" 'list_of_excluded_folders' specified but empty for configuration: %s", backup)
        else:
            for excluded_folder in listed_excluded_folders:
                excluded_path = Path(excluded_folder)
                if not excluded_path.is_absolute():
                    backup_config.list_of_excluded_folders.append(backup_config.source / excluded_path)
                else:
                    if excluded_path.is_relative_to(backup_config.source):
                        backup_config.list_of_excluded_folders.append(excluded_path)
                    else:
                        logging.warning(
                            "Excluded folder: %s is not a subpath of source: %s for configuration: %s",
                            str(excluded_path),
                            str(backup_config.source),
                            backup,
                        )
    except KeyError:
        pass


def populate_config_with_valid_quick_restore_path(config_dict: dict, backup: str, backup_config: BackupConfig) -> None:
    """Populate the backup configuration with valid quick restore path.

    Args:
        config_dict (dict): Dictionary containing the configuration data (read from a YAML file for example).
        backup (str): Key to look for in the dictionary.
        backup_config (BackupConfig): Backup configuration to populate.
    """
    try:
        listed_quick_restore_path = config_dict["backup_configurations"][backup]["quick_restore_path"]
        if listed_quick_restore_path is None:
            logging.warning(" 'quick_restore_path' specified but empty for configuration: %s", backup)
        else:
            for quick_restore_path in listed_quick_restore_path:
                quick_restore_path = Path(quick_restore_path)
                if not quick_restore_path.is_absolute():
                    backup_config.quick_restore_path.append(backup_config.source / quick_restore_path)
                else:
                    if quick_restore_path.is_relative_to(backup_config.source):
                        backup_config.quick_restore_path.append(quick_restore_path)
                    else:
                        logging.warning(
                            "Quick restore path: %s is not a subpath of source: %s for configuration: %s",
                            str(quick_restore_path),
                            str(backup_config.source),
                            backup,
                        )
    except KeyError:
        pass


def extract_valid_configuration_from_configuration_dict(config_dict: dict) -> BackupConfig:
    """Extract valid configuration from a dictionary.

    Args:
        config_dict (dict): Dictionary containing the configuration data (read from a YAML file for example).
    Returns:
        RunConfig: Dataclass containing the configuration.
    """
    run_config = RunConfig(backup_configs=[])
    if config_dict["backup_configurations"] is None:
        logging.error("No backup configurations found in the configuration file.")
        return run_config

    for backup in config_dict["backup_configurations"]:
        backup_config = BackupConfig(
            source=Path(), list_of_harddrive=[], list_of_excluded_folders=[], quick_restore_path=[]
        )
        if not is_populating_config_with_valid_source_successful(config_dict, backup, backup_config):
            continue
        if not is_populating_config_with_at_least_one_valid_list_of_harddrive_successful(
            config_dict, backup, backup_config
        ):
            continue
        populate_config_with_valid_excluded_folders(config_dict, backup, backup_config)
        populate_config_with_valid_quick_restore_path(config_dict, backup, backup_config)
        run_config.backup_configs.append(backup_config)
    return run_config


def extract_valid_configuration_from_config_file() -> RunConfig:
    """Read configuration from a YAML file and populate the RunConfig dataclass.

    This will read from the default config file in the user's configuration directory
    Not valid configurations (missing entry, or invalid path) will be logged and skipped.

    Returns:
        RunConfig: Dataclass containing the valid configurations only.
    """
    try:
        config_file_path = get_path_to_config_file_and_initialize_if_none()
        with open(config_file_path, "r", encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)
            if config_dict is None:
                logging.error("No configuration found in the configuration file: %s.", config_file_path)
                return RunConfig(backup_configs=[])
            return extract_valid_configuration_from_configuration_dict(config_dict)
    except yaml.scanner.ScannerError:
        logging.error(
            "Yaml structure of the configuration file not valid: %s",
            str(get_path_to_config_file_and_initialize_if_none().absolute()),
        )

        return RunConfig(backup_configs=[])
