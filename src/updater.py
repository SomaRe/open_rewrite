import sys
import os
import time
import shutil
import subprocess
import logging

# Basic logging for the updater script itself
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "updater.log")
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log(message):
    logging.info(message)

def main(current_exe_path, downloaded_exe_path):
    log("Updater script started.")
    log(f"Current executable: {current_exe_path}")
    log(f"Downloaded update: {downloaded_exe_path}")

    # 1. Wait for the main application to exit completely
    log("Waiting for main application to close...")
    time.sleep(3) # Adjust sleep time if needed

    # 2. Rename the current executable
    backup_exe_path = current_exe_path + ".old"
    try:
        if os.path.exists(backup_exe_path):
            log(f"Removing existing backup file: {backup_exe_path}")
            os.remove(backup_exe_path)
        log(f"Renaming {current_exe_path} to {backup_exe_path}")
        os.rename(current_exe_path, backup_exe_path)
        log("Rename successful.")
    except OSError as e:
        log(f"Error renaming current executable: {e}")
        log("Update failed: Could not rename the running application.")
        # Attempt to restore if rename failed partially? Maybe too complex.
        sys.exit(1) # Exit updater with error

    # 3. Move the downloaded executable to the original path
    try:
        log(f"Moving {downloaded_exe_path} to {current_exe_path}")
        shutil.move(downloaded_exe_path, current_exe_path)
        log("Move successful.")
    except OSError as e:
        log(f"Error moving downloaded executable: {e}")
        log("Update failed: Could not move the new version into place.")
        # Attempt to restore the backup
        try:
            log(f"Attempting to restore backup: Renaming {backup_exe_path} back to {current_exe_path}")
            os.rename(backup_exe_path, current_exe_path)
        except OSError as restore_e:
            log(f"CRITICAL ERROR: Could not restore backup: {restore_e}")
        sys.exit(1) # Exit updater with error

    # 4. Clean up the backup file (optional, keep for rollback?)
    try:
        if os.path.exists(backup_exe_path):
            log(f"Removing backup file: {backup_exe_path}")
            os.remove(backup_exe_path)
    except OSError as e:
        log(f"Warning: Could not remove backup file {backup_exe_path}: {e}")

    # 5. Restart the application
    log(f"Restarting application: {current_exe_path}")
    try:
        subprocess.Popen([current_exe_path])
        log("Application restart command issued.")
    except OSError as e:
        log(f"Error restarting application: {e}")
        log("Update completed, but failed to restart the application automatically.")
        sys.exit(1) # Exit with error, but update is technically done

    log("Updater script finished successfully.")
    sys.exit(0) # Exit updater successfully

if __name__ == "__main__":
    if len(sys.argv) != 3:
        log("Usage: updater.py <current_exe_path> <downloaded_exe_path>")
        sys.exit(1)

    current_exe = sys.argv[1]
    downloaded_exe = sys.argv[2]

    # Basic check if paths exist
    if not os.path.exists(current_exe):
        log(f"Error: Current executable path does not exist: {current_exe}")
        # sys.exit(1) # Allow proceeding, maybe it just closed
    if not os.path.exists(downloaded_exe):
        log(f"Error: Downloaded executable path does not exist: {downloaded_exe}")
        sys.exit(1)

    main(current_exe, downloaded_exe)