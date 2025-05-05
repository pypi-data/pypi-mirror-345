import os
import platform
import subprocess
import logging
from pathlib import Path
import time

log = logging.getLogger(__name__)

def run_preparation(state):
    """
    Performs environment preparation specific to Adobe Premiere Pro on Windows.
    Opens a specific template project file located on the user's desktop and maximizes the window.
    Kills existing Premiere Pro processes first.
    """
    if platform.system() != "Windows":
        log.warning("Premiere Pro preparation skipped: Not running on Windows.")
        return

    log.info(f"Premiere Pro preparation: Starting on Windows platform...")

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
        template_file = desktop_path / "template.prproj" # Changed extension
        log.info(f"Looking for template file at: {template_file}")

        template_exists = template_file.exists()
        if not template_exists:
            log.warning(f"Template file not found at: {template_file}. Will attempt to launch Premiere Pro directly.")

        # --- Kill existing Premiere Pro processes --- 
        log.info("Attempting to close existing Adobe Premiere Pro processes...")
        try:
            # Command to forcefully terminate Premiere Pro processes by image name
            # Assuming the process name includes the year for 2024 version.
            kill_cmd = ['taskkill', '/F', '/IM', 'Adobe Premiere Pro 2024.exe'] # Updated process name
            kill_result = subprocess.run(kill_cmd,
                                       capture_output=True, text=True, check=False)
            
            # Check taskkill result
            if kill_result.returncode == 0:
                log.info("Successfully sent termination signal to Adobe Premiere Pro 2024.exe processes.")
            elif "not found" in kill_result.stderr.lower() or "not found" in kill_result.stdout.lower():
                 log.info("No running Adobe Premiere Pro 2024.exe processes found to close.")
            else:
                 log.warning(f"taskkill command finished with return code {kill_result.returncode}. Output: {kill_result.stdout} Stderr: {kill_result.stderr}")
            time.sleep(2) # Increased sleep time slightly for potentially heavier app
        except FileNotFoundError:
            log.error("Error: 'taskkill' command not found. Make sure it's in the system PATH.")
        except Exception as e:
            log.error(f"Error occurred while trying to close Premiere Pro: {e}", exc_info=True)
        # --- End of kill process --- 

        # Open the file with Premiere Pro maximized on Windows
        try:
            # Explicitly quote the executable path for the start command
            pr_executable_quoted = r'"C:\Program Files\Adobe\Adobe Premiere Pro 2024\Adobe Premiere Pro.exe"'
            # Check if template exists and construct command accordingly
            if template_exists:
                log.info(f"Template file found. Attempting to open {template_file} with Premiere Pro maximized...")
                # Use empty title "" for start when executable path has spaces
                cmd = ['cmd', '/c', 'start', '/max', '""', pr_executable_quoted, str(template_file)]
            else:
                log.info(f"Template file not found. Attempting to launch Premiere Pro maximized...")
                cmd = ['cmd', '/c', 'start', '/max', '""', pr_executable_quoted]

            # Construct command as a single string for shell=True
            cmd_string = ' '.join(cmd)
            log.info(f"Executing command string with shell=True: {cmd_string}")
            print(f"[DEBUG] Attempting command string in pr_prepare: {cmd_string}")

            # Use Popen with shell=True to launch and detach
            try:
                process = subprocess.Popen(cmd_string, shell=True,
                                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                                           stdout=subprocess.DEVNULL, # Suppress any potential stdout/stderr locking
                                           stderr=subprocess.DEVNULL)
                print(f"[DEBUG] Launched process via Popen, PID (may be cmd.exe): {process.pid}")
                # Assume success if Popen doesn't throw immediately
                log.info(f"Successfully dispatched command for Premiere Pro via Popen.")
            except Exception as popen_err:
                print(f"[DEBUG] Error launching with Popen: {popen_err}")
                log.error(f"Error launching Premiere Pro with Popen: {popen_err}", exc_info=True)

            # No reliable return code check with Popen+start, assume dispatch success if no exception

        except FileNotFoundError:
             log.error("Error: 'cmd' or 'start' command not found. Ensure system PATH is configured correctly.")
        except Exception as e:
            log.error(f"Exception opening Premiere Pro on Windows: {e}", exc_info=True)
                
    except Exception as e:
        log.error(f"An unexpected error occurred during Premiere Pro preparation: {e}", exc_info=True) 