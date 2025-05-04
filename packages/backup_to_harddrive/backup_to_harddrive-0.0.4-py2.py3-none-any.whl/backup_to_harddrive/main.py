"""Main function."""

import argparse
import logging

from backup_to_harddrive.backup_from_config import run_backup_from_config_file
from backup_to_harddrive.backup_status import is_backup_switched_on, set_backup_status
from backup_to_harddrive.rsync_installation_check import (
    check_if_rsync_is_installed_and_log_if_not,
)


def return_backup_status() -> int:
    """Return the backup status.

    Returns:
        int : 2 if backup is switched off 0 if switched on.
    """
    if is_backup_switched_on():
        print("Backup is switched on.")
        return 0
    print("Backup is switched off.")
    return 2


def apply_activation_status(switch_on: int, switch_off: int):
    """Apply the activation status.

    Args:
        switch_on (int): The switch on status (1=True 0=False).
        switch_off (int): The switch off status (1=True 0=False).
    """
    if switch_on == 1:
        set_backup_status(True)
        logging.info("Backup is switched on.")
    if switch_off == 1:
        set_backup_status(False)
        logging.info("Backup is switched off.")


def main() -> int:
    """Implement main function.

    Returns:
        Int : 0 if the function runs successfully.
    """
    parser = argparse.ArgumentParser(description="Script that performs backup of home directory")
    parser.add_argument(
        "--dry-run",
        help="Perform dry run (Displays rsync commands without execution)",
        action="count",
        required=False,
        default=0,
    )
    parser.add_argument("--switch-on", help="Switch the backup functionality on", action="count")
    parser.add_argument("--switch-off", help="Switch the backup functionality off", action="count")
    parser.add_argument("--status", help="Get the status of the backup", action="count")
    args = parser.parse_args()

    dry_run = "dry_run" in args and args.dry_run == 1

    rsync_is_installed = check_if_rsync_is_installed_and_log_if_not(dry_run_enabled=dry_run)

    if "status" in args and args.status == 1:
        return return_backup_status()

    if args.switch_on == 1 or args.switch_off == 1:
        apply_activation_status(args.switch_on, args.switch_off)
        return 0

    return_value = 0
    if is_backup_switched_on() is False:
        logging.info("Backup is switched off. Exiting.")
    else:
        if rsync_is_installed is True:
            run_backup_from_config_file(dry_run=dry_run)
        else:
            logging.error("Rsync is not installed. Backup cannot be performed.")
            return_value = 1

    return return_value
