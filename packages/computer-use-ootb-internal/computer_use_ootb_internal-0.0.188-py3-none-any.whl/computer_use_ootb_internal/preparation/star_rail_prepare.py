# src/computer_use_ootb_internal/preparation/star_rail_prepare.py
import time
import platform
import subprocess # Added for taskkill
import pyautogui
import webbrowser
import logging # Use logging instead of print for better practice

# Set up logging for this module if needed, or rely on root logger
log = logging.getLogger(__name__)

def run_preparation(state):
    """
    Performs environment preparation specific to Star Rail on Windows.
    Closes existing Edge browsers, opens the specified URL in a new Edge instance,
    and performs initial clicks.
    """
    if platform.system() != "Windows":
        log.info("Star Rail preparation skipped: Not running on Windows.")
        return

    log.info("Star Rail preparation: Starting environment setup on Windows...")
    url = "https://sr.mihoyo.com/cloud/#/" # Consider making this configurable later
    browser_opened = False
    try:
        # Attempt to close existing Microsoft Edge processes
        log.info("Attempting to close existing Microsoft Edge processes...")
        try:
            # /F forces termination, /IM specifies image name
            result = subprocess.run(['taskkill', '/F', '/IM', 'msedge.exe'],
                                    capture_output=True, text=True, check=False)
            if result.returncode == 0:
                log.info("Successfully sent termination signal to msedge.exe processes.")
            elif "not found" in result.stderr.lower() or "not found" in result.stdout.lower():
                 log.info("No running msedge.exe processes found to close.")
            else:
                 log.warning(f"taskkill command finished with return code {result.returncode}. Output: {result.stdout} Stderr: {result.stderr}")
            time.sleep(2) # Give processes time to close
        except FileNotFoundError:
            log.error("Error: 'taskkill' command not found. Make sure it's in the system PATH.")
        except Exception as e:
            log.error(f"Error occurred while trying to close Edge: {e}", exc_info=True)

        # Use only webbrowser.open
        log.info(f"Attempting to open {url} using webbrowser.open()...")
        if webbrowser.open(url):
            log.info(f"Successfully requested browser to open {url} via webbrowser.open().")
            browser_opened = True
            # Ensure sleep time for browser load before clicks is present
            time.sleep(5)
        else:
            log.warning("webbrowser.open() returned False, indicating potential failure.")

        if not browser_opened:
            log.error("Failed to confirm browser opening via webbrowser.open(). Will still attempt clicks.")

        # Add pyautogui click after attempting to open the browser
        log.info("Proceeding with pyautogui actions...")
        time.sleep(5) # Wait time for the browser to load

        # Get screen size
        screen_width, screen_height = pyautogui.size()
        log.info(f"Detected screen size: {screen_width}x{screen_height}")

        # Calculate click coordinates based on a reference resolution (e.g., 1280x720)
        # TODO: Make these coordinates more robust or configurable
        click_x_1 = int(screen_width * (1036 / 1280))
        click_y_1 = int(screen_height * (500 / 720))
        log.info(f"Calculated click coordinates for starting the game: ({click_x_1}, {click_y_1})")
        click_x_2 = int(screen_width * (1233 / 1280))
        click_y_2 = int(screen_height * (30 / 720))
        log.info(f"Calculated click coordinates for closing the browser warning: ({click_x_2}, {click_y_2})")

        # Disable failsafe before clicking
        pyautogui.FAILSAFE = False
        log.info("PyAutoGUI failsafe temporarily disabled.")

        log.info(f"Clicking at coordinates: ({click_x_1}, {click_y_1})")
        pyautogui.click(click_x_1, click_y_1)
        time.sleep(2)
        pyautogui.click(click_x_1, click_y_1) # Double click?

        # Press F11 to attempt fullscreen
        log.info("Pressing F11 to enter fullscreen...")
        time.sleep(1) # Short delay before pressing F11
        pyautogui.press('f11')
        time.sleep(1)
        log.info(f"Clicking at coordinates: ({click_x_2}, {click_y_2})")
        pyautogui.click(click_x_2, click_y_2)
        time.sleep(1)
        pyautogui.click(click_x_2, click_y_2)

        log.info("Star Rail preparation clicks completed.")

    except Exception as e:
        log.error(f"Error during Star Rail preparation (browser/click): {e}", exc_info=True)
    finally:
         # Ensure failsafe is re-enabled
         pyautogui.FAILSAFE = True
         log.info("PyAutoGUI failsafe re-enabled.") 