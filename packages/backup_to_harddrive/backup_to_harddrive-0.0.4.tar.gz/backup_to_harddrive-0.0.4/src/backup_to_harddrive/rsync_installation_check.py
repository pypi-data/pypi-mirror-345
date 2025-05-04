"""Functions to check correct installation of rsync."""

import logging
import shutil

RSYNC_NOT_INSTALL_LOG_MSG = "Rsync not found in path ! Consider installing rsync with sudo apt-get install rsync"


def check_if_rsync_is_installed_and_log_if_not(dry_run_enabled: bool) -> bool:
    """Check if the rsync is installed and log if not.

    If dry_run mode is enabled, the log will be a warning.
    If dry_run mode is not enabled the log will be an error logg.
    Args:
        dry_run_enabled (bool): If dry_run mode is enabled.

    Returns:
        True if rsync is installed, False otherwise.
    """
    rsync_found = shutil.which("rsync")
    if rsync_found is None:
        if dry_run_enabled:
            logging.warning(RSYNC_NOT_INSTALL_LOG_MSG)
        else:
            logging.error(RSYNC_NOT_INSTALL_LOG_MSG)
        return False
    return True
