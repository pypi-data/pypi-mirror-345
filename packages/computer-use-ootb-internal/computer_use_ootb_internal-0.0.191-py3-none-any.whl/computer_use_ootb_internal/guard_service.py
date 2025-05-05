# src/computer_use_ootb_internal/guard_service.py
import sys
import os
import time
import logging
import subprocess
import pathlib
import ctypes
import threading # For running server thread
import queue # For queuing commands
import requests # Keep for status reporting back
import servicemanager # From pywin32
import win32serviceutil # From pywin32
import win32service # From pywin32
import win32event # From pywin32
import win32api # From pywin32
import win32process # From pywin32
import win32security # From pywin32
import win32profile # From pywin32
import win32ts # From pywin32 (Terminal Services API)
import win32con
import psutil # For process/user info
from flask import Flask, request, jsonify # For embedded server
from waitress import serve # For serving Flask app
import json # Needed for status reporting

# --- Configuration ---
_SERVICE_NAME = "OOTBGuardService"
_SERVICE_DISPLAY_NAME = "OOTB Guard Service"
_SERVICE_DESCRIPTION = "Background service for OOTB monitoring and remote management (Server POST mode)."
_PACKAGE_NAME = "computer-use-ootb-internal"
_OOTB_MODULE = "computer_use_ootb_internal.app_teachmode"
# --- Server POST Configuration ---
_LISTEN_HOST = "0.0.0.0" # Listen on all interfaces
_LISTEN_PORT = 14000 # Port for server to POST commands TO
# _SHARED_SECRET = "YOUR_SECRET_HERE" # !! REMOVED !! - No secret check implemented now
# --- End Server POST Configuration ---
_SERVER_STATUS_REPORT_URL = "http://52.160.105.102:7000/guard/status" # URL to POST status back TO (Path changed)
_LOG_FILE = pathlib.Path(os.environ['PROGRAMDATA']) / "OOTBGuardService" / "guard_post_mode.log" # Different log file
# --- End Configuration ---

_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=_LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s:%(threadName)s: %(message)s'
)

# --- Global service instance reference (needed for Flask routes) ---
_service_instance = None

# --- Flask App Definition ---
flask_app = Flask(__name__)

@flask_app.route('/command', methods=['POST'])
def receive_command():
    global _service_instance
    if not _service_instance:
        logging.error("Received command but service instance is not set.")
        return jsonify({"error": "Service not ready"}), 503

    # --- Authentication REMOVED ---
    # secret = request.headers.get('X-Guard-Secret')
    # if not secret or secret != _SHARED_SECRET:
    #     logging.warning(f"Unauthorized command POST received (Invalid/Missing X-Guard-Secret). Remote Addr: {request.remote_addr}")
    #     return jsonify({"error": "Unauthorized"}), 403
    # --- End Authentication REMOVED ---

    if not request.is_json:
        logging.warning("Received non-JSON command POST.")
        return jsonify({"error": "Request must be JSON"}), 400

    command = request.get_json()
    logging.info(f"Received command via POST: {command}")

    # Basic validation
    action = command.get("action")
    command_id = command.get("command_id", "N/A") # Use for status reporting
    if not action:
         logging.error(f"Received command POST with no action: {command}")
         return jsonify({"error": "Missing 'action' in command"}), 400

    # Queue the command for processing in a background thread
    _service_instance.command_queue.put((command_id, command))
    logging.info(f"Queued command {command_id} ({action}) for processing.")

    return jsonify({"message": f"Command {command_id} received and queued"}), 202 # Accepted

@flask_app.route('/internal/user_connected', methods=['POST'])
def user_connected_notification():
    """Internal endpoint triggered by the scheduled task helper script."""
    global _service_instance
    if not _service_instance:
        logging.error("Received user_connected signal but service instance is not set.")
        return jsonify({"error": "Service not ready"}), 503

    if not request.is_json:
        logging.warning("Received non-JSON user_connected signal.")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    username = data.get("username")
    if not username:
        logging.error("Received user_connected signal with no username.")
        return jsonify({"error": "Missing 'username' in data"}), 400

    logging.info(f"Received user_connected signal for user: {username}")

    # Call the internal start logic directly (non-blocking? or blocking?)
    # Let's make it non-blocking by putting it on the main command queue
    # This avoids holding up the signal script and uses the existing processor.
    internal_command = {
        "action": "_internal_start_ootb",
        "target_user": username
    }
    internal_command_id = f"internal_{username}_{time.time():.0f}"
    _service_instance.command_queue.put((internal_command_id, internal_command))
    logging.info(f"Queued internal start command {internal_command_id} for user {username}.")

    return jsonify({"message": "Signal received and queued"}), 202

# --- Helper Functions --- Only logging helpers needed adjustments
# Move these inside the class later
# def get_python_executable(): ...
# def get_pip_executable(): ...

# Define loggers at module level for use before instance exists?
# Or handle carefully within instance methods.

# --- PowerShell Task Scheduler Helpers --- (These will become methods) ---

# _TASK_NAME_PREFIX = "OOTB_UserLogon_" # Move to class

# def run_powershell_command(command, log_output=True): ...
# def create_or_update_logon_task(username, task_command, python_executable): ...
# def remove_logon_task(username): ...

# --- End PowerShell Task Scheduler Helpers ---

TARGET_EXECUTABLE_NAME = "computer-use-ootb-internal.exe"

class GuardService(win32serviceutil.ServiceFramework):
    _svc_name_ = _SERVICE_NAME
    _svc_display_name_ = _SERVICE_DISPLAY_NAME
    _svc_description_ = _SERVICE_DESCRIPTION
    _task_name_prefix = "OOTB_UserLogon_" # Class attribute for task prefix

    # --- Instance Logging Methods ---
    def log_info(self, msg):
        thread_name = threading.current_thread().name
        full_msg = f"[{thread_name}] {msg}"
        logging.info(full_msg)
        try:
            if threading.current_thread().name in ["MainThread", "CommandProcessor"]:
                 servicemanager.LogInfoMsg(str(full_msg))
        except Exception as e:
            # Log only to file if event log fails
            logging.warning(f"(Instance) Could not write info to Windows Event Log: {e}")

    def log_error(self, msg, exc_info=False):
        thread_name = threading.current_thread().name
        full_msg = f"[{thread_name}] {msg}"
        logging.error(full_msg, exc_info=exc_info)
        try:
            if threading.current_thread().name in ["MainThread", "CommandProcessor"]:
                servicemanager.LogErrorMsg(str(full_msg))
        except Exception as e:
            logging.warning(f"(Instance) Could not write error to Windows Event Log: {e}")
    # --- End Instance Logging --- 

    # --- Instance Helper Methods (Moved from module level) ---
    def _find_target_executable(self):
        """Finds the target executable (e.g., computer-use-ootb-internal.exe) in the Scripts directory."""
        try:
            # sys.executable should be python.exe or pythonservice.exe in the env root/Scripts
            env_dir = os.path.dirname(sys.executable)
            # If sys.executable is in Scripts, go up one level
            if os.path.basename(env_dir.lower()) == 'scripts':
                env_dir = os.path.dirname(env_dir)

            scripts_dir = os.path.join(env_dir, 'Scripts')
            target_exe_path = os.path.join(scripts_dir, TARGET_EXECUTABLE_NAME)

            self.log_info(f"_find_target_executable: Checking for executable at: {target_exe_path}")

            if os.path.exists(target_exe_path):
                self.log_info(f"_find_target_executable: Found executable: {target_exe_path}")
                # Quote if necessary for command line usage
                if " " in target_exe_path and not target_exe_path.startswith('"'):
                    return f'"{target_exe_path}"'
                return target_exe_path
            else:
                self.log_error(f"_find_target_executable: Target executable not found at {target_exe_path}")
                # Fallback: Check env root directly (less common for scripts)
                target_exe_path_root = os.path.join(env_dir, TARGET_EXECUTABLE_NAME)
                self.log_info(f"_find_target_executable: Checking fallback location: {target_exe_path_root}")
                if os.path.exists(target_exe_path_root):
                     self.log_info(f"_find_target_executable: Found executable at fallback location: {target_exe_path_root}")
                     if " " in target_exe_path_root and not target_exe_path_root.startswith('"'):
                         return f'"{target_exe_path_root}"'
                     return target_exe_path_root
                else:
                     self.log_error(f"_find_target_executable: Target executable also not found at {target_exe_path_root}")
                     return None

        except Exception as e:
            self.log_error(f"Error finding target executable: {e}")
            return None

    def __init__(self, args):
        global _service_instance
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        self.server_thread = None
        self.command_queue = queue.Queue()
        self.command_processor_thread = None
        self.session = requests.Session()

        self.target_executable_path = self._find_target_executable()
        if not self.target_executable_path:
             # Log error and potentially stop service if critical executable is missing
             self.log_error(f"CRITICAL: Could not find {TARGET_EXECUTABLE_NAME}. Service cannot function.")
             # Consider stopping the service here if needed, or handle appropriately
        else:
             self.log_info(f"Using target executable: {self.target_executable_path}")

        _service_instance = self
        # Determine path to the signal script
        self.signal_script_path = self._find_signal_script()
        self.log_info(f"Service initialized. Target executable: {self.target_executable_path}. Signal script: {self.signal_script_path}")

    def SvcStop(self):
        self.log_info(f"Service stop requested.")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        # Signal the command processor thread to stop
        self.command_queue.put(None) # Sentinel value
        # Signal the main wait loop
        win32event.SetEvent(self.hWaitStop)
        # Stopping waitress gracefully from another thread is non-trivial.
        # We rely on the SCM timeout / process termination for now.
        self.log_info(f"{_SERVICE_NAME} SvcStop: Stop signaled. Server thread will be terminated by SCM.")


    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        try:
            self.log_info(f"{_SERVICE_NAME} starting.")
            # Start the command processor thread
            self.command_processor_thread = threading.Thread(
                target=self.process_commands, name="CommandProcessor", daemon=True)
            self.command_processor_thread.start()
            self.log_info("Command processor thread started.")

            # Start the Flask server (via Waitress) in a separate thread
            self.server_thread = threading.Thread(
                target=self.run_server, name="WebServerThread", daemon=True)
            self.server_thread.start()
            self.log_info(f"Web server thread started, listening on {_LISTEN_HOST}:{_LISTEN_PORT}.")

            # Ensure logon tasks exist for predefined guest users on service start
            self.log_info("Ensuring logon tasks exist for predefined guest users (guest01-guest10)...")
            predefined_guest_users = [f"guest{i:02d}" for i in range(1, 11)] # Creates guest01, guest02, ..., guest10
            self.log_info(f"Target guest users: {predefined_guest_users}")
            
            tasks_created_count = 0
            tasks_failed_count = 0
            for username in predefined_guest_users:
                try:
                    # Call the task creation function directly
                    success = self.create_or_update_logon_task(username)
                    if success:
                        tasks_created_count += 1
                    else:
                        tasks_failed_count += 1
                        # Error is already logged within create_or_update_logon_task
                except Exception as task_create_err:
                     tasks_failed_count += 1
                     self.log_error(f"SvcDoRun: Unexpected exception creating/updating task for user {username} on startup: {task_create_err}", exc_info=True)
            
            self.log_info(f"Finished checking predefined guest users. Tasks created/updated: {tasks_created_count}, Failures: {tasks_failed_count}")

            self.log_info(f"{_SERVICE_NAME} running. Waiting for stop signal.")
            # Keep the main service thread alive waiting for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            self.log_info(f"{_SERVICE_NAME} received stop signal in main thread.")

        except Exception as e:
            self.log_error(f"Fatal error in SvcDoRun: {e}", exc_info=True)
            self.SvcStop() # Signal stop if possible
        finally:
            self.log_info(f"{_SERVICE_NAME} SvcDoRun finished.")


    def run_server(self):
        """Runs the Flask app using Waitress."""
        self.log_info(f"Waitress server starting on {_LISTEN_HOST}:{_LISTEN_PORT}")
        try:
            serve(flask_app, host=_LISTEN_HOST, port=_LISTEN_PORT, threads=4)
            self.log_info("Waitress server has stopped.") # Should only happen on shutdown
        except Exception as e:
            self.log_error(f"Web server thread encountered an error: {e}", exc_info=True)
            # Consider signaling the main thread to stop if the web server fails critically
            # For now, just log the error.


    def process_commands(self):
        """Worker thread to process commands from the queue."""
        self.log_info("Command processor thread starting.")
        while self.is_running:
            try:
                item = self.command_queue.get(block=True, timeout=1) # Add timeout to check is_running periodically
                if item is None:
                    self.log_info("Command processor received stop signal.")
                    break # Exit loop

                command_id, command = item
                action = command.get("action")
                target = command.get("target_user", "all_active")
                status = "failed_unknown" # Default status for external commands
                is_internal = action == "_internal_start_ootb" 

                self.log_info(f"Dequeued {'Internal' if is_internal else 'External'} Command ID {command_id}: action='{action}', target='{target}'")

                try:
                    if action == "update":
                        status = self.handle_update()
                    elif action == "stop_ootb":
                        status = self.handle_stop(target)
                    elif action == "start_ootb":
                        status = self.handle_start(target)
                    elif action == "_internal_start_ootb":
                        # Call the core start logic but don't report status back externally
                        internal_status = self._trigger_start_for_user(target)
                        self.log_info(f"Internal start for {target} finished with status: {internal_status}")
                        # No external status reporting for internal commands
                    else:
                        self.log_error(f"Unknown action in queue: {action}")
                        status = "failed_unknown_action"
                except Exception as handler_ex:
                    self.log_error(f"Exception processing Command ID {command_id} ({action}): {handler_ex}", exc_info=True)
                    status = "failed_exception"
                finally:
                    # Only report status for non-internal commands
                    if not is_internal:
                         self.report_command_status(command_id, status)
                    self.command_queue.task_done()

            except queue.Empty:
                # Timeout occurred, just loop again and check self.is_running
                continue
            except Exception as e:
                 self.log_error(f"Error in command processing loop: {e}", exc_info=True)
                 if self.is_running:
                     time.sleep(5)

        self.log_info("Command processor thread finished.")


    def report_command_status(self, command_id, status, details=""):
        """Sends command status back to the server."""
        if not _SERVER_STATUS_REPORT_URL:
            self.log_error("No server status report URL configured. Skipping report.")
            return

        payload = {
            "command_id": command_id,
            "status": status,
            "details": details,
            "machine_id": os.getenv('COMPUTERNAME', 'unknown_guard')
        }
        self.log_info(f"Reporting status for command {command_id}: {status}")
        try:
            response = self.session.post(_SERVER_STATUS_REPORT_URL, json=payload, timeout=15)
            response.raise_for_status()
            self.log_info(f"Status report for command {command_id} accepted by server.")
        except requests.exceptions.RequestException as e:
            self.log_error(f"Failed to report status for command {command_id}: {e}")
        except Exception as e:
             self.log_error(f"Unexpected error reporting status for command {command_id}: {e}", exc_info=True)

    # --- Command Handlers --- Now call self. for helpers

    def _get_python_executable_from_target_exe(self):
        """Attempts to find the python.exe associated with the target executable's env."""
        if not self.target_executable_path:
            self.log_error("Cannot find python.exe: target executable path is not set.")
            return None
        try:
            exe_path_unquoted = self.target_executable_path.strip('"')
            scripts_dir = os.path.dirname(exe_path_unquoted)
            # Assume target exe is in a 'Scripts' directory relative to env root
            env_dir = os.path.dirname(scripts_dir)
            if os.path.basename(scripts_dir.lower()) != 'scripts':
                self.log_warning(f"Target executable {exe_path_unquoted} not in expected 'Scripts' directory. Cannot reliably find python.exe.")
                # Fallback: maybe the target IS python.exe or next to it?
                env_dir = scripts_dir # Try assuming it's env root

            python_exe_path = os.path.join(env_dir, 'python.exe')
            self.log_info(f"Checking for python.exe at: {python_exe_path}")
            if os.path.exists(python_exe_path):
                self.log_info(f"Found associated python.exe: {python_exe_path}")
                if " " in python_exe_path and not python_exe_path.startswith('"'):
                    return f'"{python_exe_path}"'
                return python_exe_path
            else:
                self.log_error(f"Associated python.exe not found at {python_exe_path}")
                # Fallback: Check pythonw.exe?
                pythonw_exe_path = os.path.join(env_dir, 'pythonw.exe')
                if os.path.exists(pythonw_exe_path):
                    self.log_info(f"Found associated pythonw.exe as fallback: {pythonw_exe_path}")
                    if " " in pythonw_exe_path and not pythonw_exe_path.startswith('"'):
                        return f'"{pythonw_exe_path}"'
                    return pythonw_exe_path
                else:
                    self.log_error(f"Associated pythonw.exe also not found.")
                    return None

        except Exception as e:
            self.log_error(f"Error finding associated python executable: {e}")
            return None

    def handle_update(self):
        """Handles the update command by running pip install --upgrade directly."""
        self.log_info("Executing OOTB update via pip...")
        
        python_exe = self._get_python_executable_from_target_exe()
        if not python_exe:
            self.log_error("Cannot update: Could not find associated python.exe for pip.")
            return "failed_python_not_found"

        # Package name needs to be defined (replace with actual package name)
        package_name = "computer-use-ootb-internal" # Make sure this is correct
        
        # Construct the command: "C:\path\to\python.exe" -m pip install --upgrade --no-cache-dir package_name
        python_exe_unquoted = python_exe.strip('"')
        pip_args = ["-m", "pip", "install", "--upgrade", "--no-cache-dir", package_name]
        update_command_display = f'{python_exe} {" ".join(pip_args)}'

        self.log_info(f"Running update command: {update_command_display}")
        try:
            # Execute the pip command directly. Running as LocalSystem should have rights.
            result = subprocess.run(
                [python_exe_unquoted] + pip_args, 
                capture_output=True, 
                text=True, 
                check=False, # Check manually
                encoding='utf-8', 
                errors='ignore'
            )
            
            if result.stdout:
                 self.log_info(f"Update process STDOUT:\n{result.stdout.strip()}")
            if result.stderr:
                 self.log_warning(f"Update process STDERR:\n{result.stderr.strip()}")

            if result.returncode == 0:
                self.log_info("Update process completed successfully (Exit Code 0).")
                return "success"
            else:
                self.log_error(f"Update process failed (Exit Code {result.returncode}).")
                return f"failed_pip_exit_code_{result.returncode}"
                
        except FileNotFoundError:
             self.log_error(f"Update failed: Python executable not found at '{python_exe_unquoted}'.")
             return "failed_python_not_found"
        except Exception as e:
            self.log_error(f"Update failed with exception: {e}", exc_info=True)
            return "failed_exception"

    def _get_ootb_processes(self, target_user="all_active"):
        ootb_procs = []
        target_pid_list = []
        try:
            target_users = set()
            if target_user == "all_active":
                 for user_session in psutil.users():
                      username = user_session.name.split('\\')[-1]
                      target_users.add(username.lower())
            else:
                 target_users.add(target_user.lower())
            self.log_info(f"Searching for OOTB processes for users: {target_users}")
            
            # Use the potentially corrected python.exe path for matching
            python_exe_path_for_check = self.target_executable_path.strip('"') 
            self.log_info(f"_get_ootb_processes: Checking against python path: {python_exe_path_for_check}")

            for proc in psutil.process_iter(['pid', 'name', 'username', 'cmdline', 'exe']):
                try:
                    pinfo = proc.info
                    proc_username = pinfo['username']
                    if proc_username:
                        proc_username = proc_username.split('\\')[-1].lower()

                    if proc_username in target_users:
                        cmdline = ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
                        # Check if the process executable matches our corrected python path AND module is in cmdline
                        if pinfo['exe'] and pinfo['exe'] == python_exe_path_for_check and _OOTB_MODULE in cmdline:
                            self.log_info(f"Found matching OOTB process: PID={pinfo['pid']}, User={pinfo['username']}, Cmd={cmdline}")
                            ootb_procs.append(proc)
                            target_pid_list.append(pinfo['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            self.log_info(f"Found {len(ootb_procs)} OOTB process(es) matching criteria: {target_pid_list}")
        except Exception as e:
             self.log_error(f"Error enumerating processes: {e}", exc_info=True)
        return ootb_procs

    def handle_stop(self, target_user="all_active"):
        """Stops the OOTB process for specified user(s). Uses psutil first, then taskkill fallback."""
        self.log_info(f"Executing stop OOTB for target '{target_user}'...")
        stopped_count_psutil = 0
        stopped_count_taskkill = 0
        errors = []
        
        target_users_lower = set()
        if target_user == "all_active":
            try:
                for user_session in psutil.users():
                    username_lower = user_session.name.split('\\')[-1].lower()
                    target_users_lower.add(username_lower)
                self.log_info(f"Targeting all users found by psutil: {target_users_lower}")
            except Exception as e:
                 self.log_error(f"Could not list users via psutil for stop all: {e}")
                 errors.append("failed_user_enumeration")
                 target_users_lower = set() # Avoid proceeding if user list failed
        else:
            target_users_lower.add(target_user.lower())
            self.log_info(f"Targeting specific user: {target_user.lower()}")

        if not target_users_lower and target_user == "all_active":
             self.log_info("No active users found to stop.")
             # If specific user targeted, proceed even if psutil didn't list them (maybe inactive)

        procs_to_kill_by_user = {user: [] for user in target_users_lower}
        
        # --- Attempt 1: psutil find and terminate ---
        self.log_info("Attempting stop using psutil...")
        try:
            all_running = self._get_ootb_processes("all") # Get all regardless of user first
            for proc in all_running:
                try:
                    proc_user = proc.info.get('username')
                    if proc_user:
                         user_lower = proc_user.split('\\')[-1].lower()
                         if user_lower in target_users_lower:
                              procs_to_kill_by_user[user_lower].append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                     pass # Process ended or we can't access it
        except Exception as e:
             self.log_error(f"Error getting process list for psutil stop: {e}")
             errors.append("failed_psutil_list")

        for user, procs in procs_to_kill_by_user.items():
            if not procs:
                self.log_info(f"psutil: No OOTB processes found running for user '{user}'.")
                continue
            
            self.log_info(f"psutil: Found {len(procs)} OOTB process(es) for user '{user}'. Attempting terminate...")
            for proc in procs:
                try:
                    pid = proc.pid
                    self.log_info(f"psutil: Terminating PID {pid} for user '{user}'...")
                    proc.terminate()
                    try:
                         proc.wait(timeout=3) # Wait a bit for termination
                         self.log_info(f"psutil: PID {pid} terminated successfully.")
                         stopped_count_psutil += 1
                    except psutil.TimeoutExpired:
                         self.log_warning(f"psutil: PID {pid} did not terminate within timeout. Will try taskkill.")
                         # No error append yet, let taskkill try
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                         self.log_info(f"psutil: PID {pid} already gone or access denied after terminate.")
                         stopped_count_psutil += 1 # Count it as stopped
                except (psutil.NoSuchProcess, psutil.AccessDenied) as term_err:
                     self.log_warning(f"psutil: Error terminating PID {proc.pid if 'proc' in locals() and proc else 'unknown'}: {term_err}. It might be gone already.")
                     # If it's gone, count it?
                     stopped_count_psutil += 1 # Assume it's gone if NoSuchProcess
                except Exception as term_ex:
                     self.log_error(f"psutil: Unexpected error terminating PID {proc.pid if 'proc' in locals() and proc else 'unknown'}: {term_ex}")
                     errors.append(f"failed_psutil_terminate_{user}")

        # --- Attempt 2: taskkill fallback (for users where psutil didn't find/stop) ---
        # Only run taskkill if psutil didn't stop anything for a specific user OR if target was specific user
        
        if not self.target_executable_path:
             errors.append("skipped_taskkill_no_exe_path")
        else:
            executable_name = os.path.basename(self.target_executable_path.strip('"'))
            for user in target_users_lower:
                run_taskkill = False
                if user not in procs_to_kill_by_user or not procs_to_kill_by_user[user]:
                    # psutil didn't find anything for this user initially
                    run_taskkill = True 
                    self.log_info(f"taskkill: psutil found no processes for '{user}', attempting taskkill as fallback.")
                elif any(p.is_running() for p in procs_to_kill_by_user.get(user, []) if p): # Check if any psutil targets still running
                    run_taskkill = True
                    self.log_info(f"taskkill: Some processes for '{user}' may remain after psutil, attempting taskkill cleanup.")
                
                if run_taskkill:
                    # Construct taskkill command
                    # Username format might need adjustment (e.g., DOMAIN\user). Try simple first.
                    taskkill_command = [
                        "taskkill", "/F", # Force
                        "/IM", executable_name, # Image name
                        "/FI", f"USERNAME eq {user}" # Filter by username
                    ]
                    self.log_info(f"Running taskkill command: {' '.join(taskkill_command)}")
                    try:
                        result = subprocess.run(taskkill_command, capture_output=True, text=True, check=False)
                        if result.returncode == 0:
                             self.log_info(f"taskkill successful for user '{user}' (Exit Code 0).")
                             # Can't easily count how many were killed here, assume success if exit 0
                             stopped_count_taskkill += 1 # Indicate taskkill ran successfully for user
                        elif result.returncode == 128: # Code 128: No tasks found matching criteria
                             self.log_info(f"taskkill: No matching processes found for user '{user}'.")
                        else:
                             self.log_error(f"taskkill failed for user '{user}' (Exit Code {result.returncode}).")
                             self.log_error(f"  taskkill STDOUT: {result.stdout.strip()}")
                             self.log_error(f"  taskkill STDERR: {result.stderr.strip()}")
                             errors.append(f"failed_taskkill_{user}")
                    except FileNotFoundError:
                         self.log_error("taskkill command not found.")
                         errors.append("failed_taskkill_not_found")
                         break # Stop trying taskkill if command is missing
                    except Exception as tk_ex:
                         self.log_error(f"Exception running taskkill for '{user}': {tk_ex}")
                         errors.append(f"failed_taskkill_exception_{user}")

        # --- Consolidate status --- 
        final_status = "failed" # Default to failed if errors occurred
        if stopped_count_psutil > 0 or stopped_count_taskkill > 0:
             final_status = "success" if not errors else "partial_success"
        elif not errors:
             final_status = "success_no_processes_found"
        
        details = f"psutil_stopped={stopped_count_psutil}, taskkill_users_attempted={stopped_count_taskkill}, errors={len(errors)}"
        self.log_info(f"Finished stopping OOTB. Status: {final_status}. Details: {details}")
        return f"{final_status}::{details}" # Return status and details

    def handle_start(self, target_user="all_active"):
        """Handles external start command request (finds users, calls internal trigger)."""
        self.log_info(f"External start requested for target '{target_user}'...")
        # This function now primarily identifies target users and calls the internal trigger method.
        # The status returned here reflects the process of identifying and triggering,
        # not necessarily the final success/failure of the actual start (which happens async).
        
        active_sessions = {} # user_lower: session_id
        all_system_users = set() # user_lower
        try:
            # Use psutil for system user list, WTS for active sessions/IDs
            for user_session in psutil.users():
                username_lower = user_session.name.split('\\')[-1].lower()
                all_system_users.add(username_lower)
            
            sessions = win32ts.WTSEnumerateSessions(win32ts.WTS_CURRENT_SERVER_HANDLE)
            for session in sessions:
                if session['State'] == win32ts.WTSActive:
                    try:
                        user = win32ts.WTSQuerySessionInformation(win32ts.WTS_CURRENT_SERVER_HANDLE, session['SessionId'], win32ts.WTSUserName)
                        if user:
                            active_sessions[user.lower()] = session['SessionId']
                    except Exception as query_err:
                        self.log_error(f"Could not query session {session['SessionId']}: {query_err}")
        except Exception as user_enum_err:
             self.log_error(f"Error enumerating users/sessions: {user_enum_err}", exc_info=True)
             return "failed_user_enumeration"

        target_users_normalized = set()
        if target_user == "all_active":
             target_users_normalized = set(active_sessions.keys())
             self.log_info(f"Targeting all active users for start: {target_users_normalized}")
        else:
             normalized_target = target_user.lower()
             target_users_normalized.add(normalized_target)
             self.log_info(f"Targeting specific user for start: {normalized_target}")

        if not target_users_normalized:
             self.log_info("No target users identified for start.")
             return "failed_no_target_users"
        
        trigger_results = {}
        for user in target_users_normalized:
             self.log_info(f"Calling internal start trigger for user: {user}")
             # Call the core logic directly (this is now synchronous within the handler)
             # Or queue it? Queuing might be better to avoid blocking the handler if many users.
             # Let's stick to the queue approach from the internal endpoint:
             internal_command = {
                "action": "_internal_start_ootb",
                "target_user": user
             }
             internal_command_id = f"external_{user}_{time.time():.0f}"
             self.command_queue.put((internal_command_id, internal_command))
             trigger_results[user] = "queued"

        self.log_info(f"Finished queuing start triggers. Results: {trigger_results}")
        # The status here just means we successfully queued the actions
        # Actual success/failure happens in the command processor later.
        # We might need a different way to report overall status if needed.
        return f"success_queued::{json.dumps(trigger_results)}" 


    def _trigger_start_for_user(self, username):
        """Core logic to start OOTB for a single user. Called internally."""
        user = username.lower() # Ensure lowercase
        self.log_info(f"Internal trigger: Starting OOTB check for user '{user}'...")
        task_created_status = "task_unknown"
        immediate_start_status = "start_not_attempted"
        final_status = "failed_unknown"

        try:
            # 1. Ensure scheduled task exists (still useful fallback/persistence)
            try:
                task_created = self.create_or_update_logon_task(user)
                task_created_status = "task_success" if task_created else "task_failed"
            except Exception as task_err:
                 self.log_error(f"Internal trigger: Exception creating/updating task for {user}: {task_err}", exc_info=True)
                 task_created_status = "task_exception"
                 # Don't necessarily fail the whole operation yet
            
            # 2. Check if user is active
            active_sessions = {} # Re-check active sessions specifically for this user
            session_id = None
            token = None
            is_active = False
            try:
                sessions = win32ts.WTSEnumerateSessions(win32ts.WTS_CURRENT_SERVER_HANDLE)
                for session in sessions:
                    if session['State'] == win32ts.WTSActive:
                        try:
                            current_user = win32ts.WTSQuerySessionInformation(win32ts.WTS_CURRENT_SERVER_HANDLE, session['SessionId'], win32ts.WTSUserName)
                            if current_user and current_user.lower() == user:
                                session_id = session['SessionId']
                                is_active = True
                                self.log_info(f"Internal trigger: User '{user}' is active in session {session_id}.")
                                break
                        except Exception: pass # Ignore errors querying other sessions
            except Exception as e:
                 self.log_error(f"Internal trigger: Error checking active sessions for {user}: {e}")
                 # Continue, assume inactive if check failed?
            
            if not is_active:
                self.log_info(f"Internal trigger: User '{user}' is not active. Skipping immediate start.")
                immediate_start_status = "start_skipped_inactive"
                final_status = task_created_status # Status depends only on task creation
                return final_status # Exit early if inactive

            # 3. Check if already running for this active user
            is_running = False
            try:
                running_procs = self._get_ootb_processes(user)
                if running_procs:
                     is_running = True
                     self.log_info(f"Internal trigger: OOTB already running for active user '{user}'. Skipping immediate start.")
                     immediate_start_status = "start_skipped_already_running"
                     final_status = "success_already_running" # Considered success
                     return final_status # Exit early if already running
            except Exception as e:
                 self.log_error(f"Internal trigger: Error checking existing processes for {user}: {e}")
                 # Continue and attempt start despite error?

            # 4. Attempt immediate start (User is active and not running)
            immediate_start_status = "start_attempted"
            self.log_info(f"Internal trigger: User '{user}' is active and not running. Attempting immediate start via CreateProcessAsUser...")
            try:
                token = win32ts.WTSQueryUserToken(session_id)
                env = win32profile.CreateEnvironmentBlock(token, False)
                startup = win32process.STARTUPINFO()
                creation_flags = 0x00000010 # CREATE_NEW_CONSOLE
                lpApplicationName = None
                lpCommandLine = f'cmd.exe /K "{self.target_executable_path}"'
                cwd = os.path.dirname(self.target_executable_path.strip('"')) if os.path.dirname(self.target_executable_path.strip('"')) != '' else None

                # Log details before call
                self.log_info(f"Internal trigger: Calling CreateProcessAsUser:")
                self.log_info(f"  lpCommandLine: {lpCommandLine}")
                self.log_info(f"  lpCurrentDirectory: {cwd if cwd else 'Default'}")

                hProcess, hThread, dwPid, dwTid = win32process.CreateProcessAsUser(
                    token, lpApplicationName, lpCommandLine, None, None, False,
                    creation_flags, env, cwd, startup
                )
                self.log_info(f"Internal trigger: CreateProcessAsUser call succeeded for user '{user}' (PID: {dwPid}). Checking existence...")
                win32api.CloseHandle(hProcess)
                win32api.CloseHandle(hThread)

                time.sleep(1)
                if psutil.pid_exists(dwPid):
                    self.log_info(f"Internal trigger: Immediate start succeeded for user '{user}' (PID {dwPid}).")
                    immediate_start_status = "start_success"
                    final_status = "success" # Overall success
                else:
                    self.log_error(f"Internal trigger: Immediate start failed for user '{user}': Process {dwPid} exited immediately.")
                    immediate_start_status = "start_failed_exited"
                    final_status = "failed_start_exited"

            except Exception as proc_err:
                 self.log_error(f"Internal trigger: Exception during CreateProcessAsUser for user '{user}': {proc_err}", exc_info=True)
                 immediate_start_status = "start_failed_exception"
                 final_status = "failed_start_exception"
            finally:
                 if token: win32api.CloseHandle(token)
            
            # Combine results (though mostly determined by start attempt now)
            # Example: final_status = f"{task_created_status}_{immediate_start_status}"
            return final_status

        except Exception as e:
             self.log_error(f"Internal trigger: Unexpected error processing start for {username}: {e}", exc_info=True)
             return "failed_trigger_exception"


    def create_or_update_logon_task(self, username):
        """Creates/updates task to trigger the internal signal script on session connect."""
        if not self.signal_script_path:
            self.log_error(f"Cannot create task for {username}: Signal script path is not set.")
            return False
        if not sys.executable:
             self.log_error(f"Cannot create task for {username}: sys.executable is not found.")
             return False
        
        # Find the correct python.exe/pythonw.exe from the environment
        python_exe = self._get_python_executable_from_target_exe()
        if not python_exe:
            self.log_error(f"Cannot create task for {username}: Failed to find associated python executable via _get_python_executable_from_target_exe.")
            return False

        # Prepare paths and arguments carefully for PowerShell
        action_executable_path = python_exe.strip("'\"") # Remove potential existing quotes
        script_path = self.signal_script_path.strip("'\"")
        user_arg = username # Assuming username has no special chars needing escape within PS
        
        # Ensure script path is quoted if needed
        quoted_script_path = f'""{script_path}""' if ' ' in script_path else script_path # Use "" for literal quotes inside PS string
        # Username might need quoting if it contains spaces, though unlikely
        # Construct the argument string passed TO python.exe: "script_path" username
        python_arguments = f'{quoted_script_path} {user_arg}'
        
        # Working directory for the script (likely its own directory)
        try:
            script_dir = os.path.dirname(script_path)
            if not script_dir: script_dir = "."
            # Escape single quotes for PowerShell string literal
            ps_escaped_working_directory = script_dir.replace("'", "''") 
            working_directory_setting = f"$action.WorkingDirectory = '{ps_escaped_working_directory}'"
        except Exception as e:
             self.log_error(f"Error determining working directory for signal script task: {e}. WD will not be set.")
             working_directory_setting = "# Could not set WorkingDirectory"

        # Escape paths and args for embedding in PowerShell command string
        ps_escaped_executable = action_executable_path.replace("'", "''")
        ps_escaped_arguments = python_arguments.replace("'", "''")
        ps_escaped_username = username.replace("'", "''")
        task_name = f"OOTB_UserConnect_{username}"
        
        # PowerShell command construction
        ps_command = f"""
        $taskName = \"{task_name}\"
        $principal = New-ScheduledTaskPrincipal -UserId '{ps_escaped_username}' -LogonType Interactive
        
        # Action: Run python signal script
        $action = New-ScheduledTaskAction -Execute '{ps_escaped_executable}' -Argument '{ps_escaped_arguments}'
        {working_directory_setting}

        # Trigger: At Logon for the specified user
        $trigger = New-ScheduledTaskTrigger -AtLogOn
        # Optional: Add delay if needed (e.g., after desktop loads)
        # $trigger.Delay = 'PT15S'
        
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 9999) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
        $description = "Triggers OOTB Guard Service for user {username} upon logon via internal signal." # Updated description

        # Unregister existing task first (force)
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

        # Register the new task
        Register-ScheduledTask -TaskName $taskName -Principal $principal -Action $action -Trigger $trigger -Settings $settings -Description $description -Force
        """
        self.log_info(f"Attempting to create/update task '{task_name}' for user '{username}' to run signal script.")
        try:
            success = self.run_powershell_command(ps_command)
            if success:
                 self.log_info(f"Successfully ran PowerShell command to create/update task '{task_name}'.")
                 return True
            else:
                 self.log_error(f"PowerShell command failed to create/update task '{task_name}'. See previous logs.")
                 return False
        except Exception as e:
            self.log_error(f"Failed to create/update scheduled task '{task_name}' for user '{username}': {e}", exc_info=True)
            return False

    def run_powershell_command(self, command, log_output=True):
        """Executes a PowerShell command and handles output/errors. Returns True on success."""
        self.log_info(f"Executing PowerShell: {command}")
        try:
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore'
            )
            if log_output and result.stdout:
                self.log_info(f"PowerShell STDOUT:\n{result.stdout.strip()}")
            if log_output and result.stderr:
                # Log stderr as info, as some commands write status here (like unregister task not found)
                self.log_info(f"PowerShell STDERR:\n{result.stderr.strip()}") 
            return True
        except FileNotFoundError:
            self.log_error("'powershell.exe' not found. Cannot manage scheduled tasks.")
            return False
        except subprocess.CalledProcessError as e:
            # Log error but still return False, handled by caller
            self.log_error(f"PowerShell command failed (Exit Code {e.returncode}):")
            self.log_error(f"  Command: {e.cmd}")
            if e.stdout: self.log_error(f"  STDOUT: {e.stdout.strip()}")
            if e.stderr: self.log_error(f"  STDERR: {e.stderr.strip()}")
            return False
        except Exception as e:
            self.log_error(f"Unexpected error running PowerShell: {e}", exc_info=True)
            return False

    def remove_logon_task(self, username):
        """Removes the logon scheduled task for a user."""
        task_name = f"{self._task_name_prefix}{username}"
        safe_task_name = task_name.replace("'", "''")
        command = f"Unregister-ScheduledTask -TaskName '{safe_task_name}' -Confirm:$false -ErrorAction SilentlyContinue"
        self.run_powershell_command(command, log_output=False)
        self.log_info(f"Attempted removal of scheduled task '{task_name}' for user '{username}'.")
        return True

    def _find_signal_script(self):
        """Finds the signal_connection.py script relative to this service file."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(base_dir, "signal_connection.py")
            if os.path.exists(script_path):
                self.log_info(f"Found signal script at: {script_path}")
                # Quote if needed?
                if " " in script_path and not script_path.startswith('"'):
                    return f'"{script_path}"'
                return script_path
            else:
                self.log_error(f"Signal script signal_connection.py not found near {base_dir}")
                return None
        except Exception as e:
            self.log_error(f"Error finding signal script: {e}")
            return None

# --- Main Execution Block ---
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        self.log_info("Starting service in debug mode...")
        print(f"Running Flask server via Waitress on {_LISTEN_HOST}:{_LISTEN_PORT} for debugging...")
        print("Service logic (command processing) will NOT run in this mode.")
        print("Use this primarily to test the '/command' endpoint receiving POSTs.")
        print("Press Ctrl+C to stop.")
        try:
             serve(flask_app, host=_LISTEN_HOST, port=_LISTEN_PORT, threads=1)
        except KeyboardInterrupt:
             print("\nDebug server stopped.")

    elif len(sys.argv) == 1:
        try:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(GuardService)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            import winerror
            if details.winerror == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                print(f"Error: Not started by SCM.")
                print(f"Use 'python {os.path.basename(__file__)} install|start|stop|remove|debug'")
            else:
                print(f"Error preparing service: {details}")
        except Exception as e:
             print(f"Unexpected error initializing service: {e}")
    else:
        win32serviceutil.HandleCommandLine(GuardService) 