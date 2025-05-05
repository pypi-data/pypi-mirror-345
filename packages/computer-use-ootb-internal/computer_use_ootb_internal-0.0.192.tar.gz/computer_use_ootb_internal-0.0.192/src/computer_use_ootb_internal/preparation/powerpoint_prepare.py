import os
import platform
import subprocess
import logging
from pathlib import Path
import time

log = logging.getLogger(__name__)

def run_preparation(state):
    """
    Performs environment preparation specific to PowerPoint on Windows.
    Opens a specific template file located on the user's desktop and maximizes the window.
    """
    if platform.system() != "Windows":
        log.warning("PowerPoint preparation skipped: Not running on Windows.")
        return

    log.info(f"PowerPoint preparation: Starting on Windows platform...")

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
        template_file = desktop_path / "template.pptx"
        log.info(f"Looking for template file at: {template_file}")

        template_exists = template_file.exists()
        if not template_exists:
             log.warning(f"Template file not found at: {template_file}. Will attempt to launch PowerPoint directly.")

        # --- Kill existing PowerPoint processes --- 
        log.info("Attempting to close existing Microsoft PowerPoint processes...")
        try:
            # Command to forcefully terminate PowerPoint processes by image name
            kill_cmd = ['taskkill', '/F', '/IM', 'POWERPNT.EXE']
            kill_result = subprocess.run(kill_cmd,
                                       capture_output=True, text=True, check=False)
            
            # Check taskkill result
            if kill_result.returncode == 0:
                log.info("Successfully sent termination signal to POWERPNT.EXE processes.")
            elif "not found" in kill_result.stderr.lower() or "not found" in kill_result.stdout.lower():
                 log.info("No running POWERPNT.EXE processes found to close.")
            else:
                 # Log potential issues if taskkill ran but didn't return 0 or expected "not found" message
                 log.warning(f"taskkill command finished with return code {kill_result.returncode}. Output: {kill_result.stdout} Stderr: {kill_result.stderr}")
            # Add a small delay to allow processes to close
            time.sleep(2) 
        except FileNotFoundError:
            log.error("Error: 'taskkill' command not found. Make sure it's in the system PATH.")
        except Exception as e:
            # Catch other potential errors during taskkill execution
            log.error(f"Error occurred while trying to close PowerPoint: {e}", exc_info=True)
        # --- End of kill process --- 

        # Open the file with PowerPoint maximized on Windows
        try:
            # Check if template exists and construct command accordingly
            if template_file.exists():
                log.info(f"Template file found. Attempting to open {template_file} with PowerPoint maximized...")
                cmd = ['cmd', '/c', 'start', '/max', 'powerpnt', str(template_file)]
            else:
                log.info(f"Template file not found. Attempting to launch PowerPoint maximized...")
                cmd = ['cmd', '/c', 'start', '/max', 'powerpnt']

            log.info(f"Executing command: {' '.join(cmd)}")
            print(f"[DEBUG] Attempting command in powerpoint_prepare: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=False, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

            # ADDED PRINTS for result
            print(f"[DEBUG] powerpoint_prepare command result:")
            print(f"[DEBUG]   Return Code: {result.returncode}")
            print(f"[DEBUG]   Stdout: {result.stdout.strip() if result.stdout else ''}")
            print(f"[DEBUG]   Stderr: {result.stderr.strip() if result.stderr else ''}")

            if result.returncode == 0:
                log.info(f"Successfully executed command for PowerPoint.")
            else:
                log.error(f"Error opening PowerPoint: {result.stderr.strip()}")
                if result.stdout:
                    log.error(f"Stdout from start command: {result.stdout.strip()}")
        except FileNotFoundError:
             log.error("Error: 'cmd' or 'start' command not found. Ensure system PATH is configured correctly.")
        except Exception as e:
            log.error(f"Exception opening PowerPoint on Windows: {e}", exc_info=True)
                
    except Exception as e:
        log.error(f"An unexpected error occurred during PowerPoint preparation: {e}", exc_info=True) 