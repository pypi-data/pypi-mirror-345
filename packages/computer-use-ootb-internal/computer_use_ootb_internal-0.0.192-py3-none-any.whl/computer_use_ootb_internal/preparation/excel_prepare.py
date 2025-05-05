import os
import platform
import subprocess
import logging
from pathlib import Path
import time

log = logging.getLogger(__name__)

def run_preparation(state):
    """
    Performs environment preparation specific to Excel on Windows.
    Opens a specific template file located on the user's desktop and maximizes the window.
    Kills existing Excel processes first.
    """
    if platform.system() != "Windows":
        log.warning("Excel preparation skipped: Not running on Windows.")
        return

    log.info(f"Excel preparation: Starting on Windows platform...")

    try:
        # Determine the desktop path for Windows
        try:
            username = os.environ.get("USERNAME", "")
            if not username:
                log.error("Could not determine Windows username from environment")
                return
            
            log.info(f"Using Windows username: {username}")
            desktop_path = Path(f"C:/Users/{username}/Desktop")
            
            if not desktop_path.exists():
                log.error(f"Desktop path not found at: {desktop_path}")
                alt_path = Path(f"C:/Documents and Settings/{username}/Desktop")
                if alt_path.exists():
                    desktop_path = alt_path
                    log.info(f"Using alternative desktop path: {desktop_path}")
                else:
                    log.error("Failed to find user's desktop directory")
                    return
            
        except Exception as e:
            log.error(f"Error determining Windows user desktop: {e}", exc_info=True)
            return
            
        # Construct path to template file
        template_file = desktop_path / "template.xlsx" # Changed extension
        log.info(f"Looking for template file at: {template_file}")

        template_exists = template_file.exists()
        if not template_exists:
            log.warning(f"Template file not found at: {template_file}. Will attempt to launch Excel directly.")

        # --- Kill existing Excel processes --- 
        log.info("Attempting to close existing Microsoft Excel processes...")
        try:
            # Command to forcefully terminate Excel processes by image name
            kill_cmd = ['taskkill', '/F', '/IM', 'EXCEL.EXE'] # Changed process name
            kill_result = subprocess.run(kill_cmd,
                                       capture_output=True, text=True, check=False)
            
            # Check taskkill result
            if kill_result.returncode == 0:
                log.info("Successfully sent termination signal to EXCEL.EXE processes.")
            elif "not found" in kill_result.stderr.lower() or "not found" in kill_result.stdout.lower():
                 log.info("No running EXCEL.EXE processes found to close.")
            else:
                 log.warning(f"taskkill command finished with return code {kill_result.returncode}. Output: {kill_result.stdout} Stderr: {kill_result.stderr}")
            time.sleep(2) 
        except FileNotFoundError:
            log.error("Error: 'taskkill' command not found. Make sure it's in the system PATH.")
        except Exception as e:
            log.error(f"Error occurred while trying to close Excel: {e}", exc_info=True)
        # --- End of kill process --- 

        # Open the file with Excel maximized on Windows
        try:
            # Check if template exists and construct command accordingly
            if template_file.exists():
                log.info(f"Template file found. Attempting to open {template_file} with Excel maximized...")
                cmd = ['cmd', '/c', 'start', '/max', 'excel', str(template_file)]
            else:
                log.info(f"Template file not found. Attempting to launch Excel maximized...")
                cmd = ['cmd', '/c', 'start', '/max', 'excel']

            log.info(f"Executing command: {' '.join(cmd)}")
            print(f"[DEBUG] Attempting command in excel_prepare: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=False, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

            # ADDED PRINTS for result
            print(f"[DEBUG] excel_prepare command result:")
            print(f"[DEBUG]   Return Code: {result.returncode}")
            print(f"[DEBUG]   Stdout: {result.stdout.strip() if result.stdout else ''}")
            print(f"[DEBUG]   Stderr: {result.stderr.strip() if result.stderr else ''}")

            if result.returncode == 0:
                log.info(f"Successfully executed command for Excel.")
            else:
                log.error(f"Error opening Excel: {result.stderr.strip()}")
                if result.stdout:
                    log.error(f"Stdout from start command: {result.stdout.strip()}")
        except FileNotFoundError:
             log.error("Error: 'cmd' or 'start' command not found. Ensure system PATH is configured correctly.")
        except Exception as e:
            log.error(f"Exception opening Excel on Windows: {e}", exc_info=True)
                
    except Exception as e:
        log.error(f"An unexpected error occurred during Excel preparation: {e}", exc_info=True) 