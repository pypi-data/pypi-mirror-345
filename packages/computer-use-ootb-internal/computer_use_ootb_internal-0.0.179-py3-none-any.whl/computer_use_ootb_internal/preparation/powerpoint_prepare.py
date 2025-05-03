import os
import platform
import subprocess
import logging
from pathlib import Path

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

        if not template_file.exists():
            log.error(f"Template file not found at: {template_file}")
            return

        # Open the file with PowerPoint maximized on Windows
        log.info(f"Attempting to open {template_file} with PowerPoint maximized on Windows...")
        try:
            # Use start command with /max flag on Windows
            cmd = ['cmd', '/c', 'start', '/max', 'powerpnt', str(template_file)]
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            
            if result.returncode == 0:
                log.info(f"Successfully launched PowerPoint maximized with {template_file}")
            else:
                # Log stderr for debugging potential start command issues
                log.error(f"Error opening PowerPoint: {result.stderr.strip()}")
                # Also log stdout as start command might output info there
                if result.stdout:
                    log.error(f"Stdout from start command: {result.stdout.strip()}")
        except FileNotFoundError:
             log.error("Error: 'cmd' or 'start' command not found. Ensure system PATH is configured correctly.")
        except Exception as e:
            log.error(f"Exception opening PowerPoint on Windows: {e}", exc_info=True)
                
    except Exception as e:
        log.error(f"An unexpected error occurred during PowerPoint preparation: {e}", exc_info=True) 