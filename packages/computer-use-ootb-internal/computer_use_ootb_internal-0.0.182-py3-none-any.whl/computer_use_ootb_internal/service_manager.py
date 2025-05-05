# src/computer_use_ootb_internal/service_manager.py
import sys
import os
import inspect
import subprocess
import ctypes
import platform
import time

# Constants need to match guard_service.py
_SERVICE_NAME = "OOTBGuardService"
_SERVICE_DISPLAY_NAME = "OOTB Guard Service"
_TASK_NAME_PREFIX = "OOTB_UserLogon_" # Must match guard_service.py

def is_admin():
    """Check if the script is running with administrative privileges."""
    if platform.system() != "Windows":
        return False # Only applicable on Windows
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_service_module_path():
    """Gets the absolute path to the guard_service.py module."""
    # Find the path relative to this script's location
    # This assumes service_manager.py and guard_service.py are in the same installed package directory
    try:
        current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        service_module = os.path.join(current_dir, "guard_service.py")
        if not os.path.exists(service_module):
            raise FileNotFoundError(f"guard_service.py not found adjacent to service_manager.py in {current_dir}")
        return service_module
    except Exception as e:
         # Fallback if inspect fails (e.g., in some frozen environments)
         # Try finding it relative to the script itself? Unreliable.
         # Let's try sys.prefix - might work in standard venv/conda installs
         try:
             # sys.prefix points to the environment root (e.g., C:\path\to\env)
             # Package likely installed in Lib\site-packages\<package_name>
             # This depends heavily on installation layout
             package_name = __name__.split('.')[0] # Should be 'computer_use_ootb_internal'
             site_packages_path = os.path.join(sys.prefix, 'Lib', 'site-packages')
             module_dir = os.path.join(site_packages_path, package_name)
             service_module = os.path.join(module_dir, "guard_service.py")
             if os.path.exists(service_module):
                 print(f"Warning: Found service module via sys.prefix fallback: {service_module}")
                 return service_module
             else:
                 raise FileNotFoundError(f"guard_service.py not found via inspect or sys.prefix fallback (checked {module_dir})")
         except Exception as fallback_e:
             raise FileNotFoundError(f"Could not find guard_service.py using inspect ({e}) or sys.prefix ({fallback_e}). Check installation.")


def run_service_command(command_args, check_errors=True):
    """Runs the guard_service.py script with specified command-line args."""
    if not is_admin():
        print("Error: Administrative privileges are required to manage the service.", file=sys.stderr)
        print("Please run this command from an Administrator Command Prompt or PowerShell.", file=sys.stderr)
        return False

    try:
        python_exe = sys.executable # Use the same python that's running this script
        service_script = get_service_module_path()
    except FileNotFoundError as e:
         print(f"Error: {e}", file=sys.stderr)
         return False

    # Quote paths if they contain spaces
    if " " in python_exe and not python_exe.startswith('"'):
        python_exe = f'"{python_exe}"'
    if " " in service_script and not service_script.startswith('"'):
        service_script = f'"{service_script}"'

    # Construct command using list to avoid shell quoting issues
    cmd = [sys.executable, get_service_module_path()] + command_args
    print(f"Executing command: {' '.join(cmd)}")

    try:
        # Run the command. Use shell=False with list of args.
        # Capture output to check for specific errors if needed, but print it too.
        result = subprocess.run(cmd, capture_output=True, text=True, check=check_errors, encoding='utf-8')
        if result.stdout:
            print("Command STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("Command STDERR:")
            print(result.stderr)
        print(f"Command {' '.join(command_args)} executed successfully.")
        return True
    except FileNotFoundError as e:
         print(f"Error: Could not find Python executable or service script during execution.", file=sys.stderr)
         print(f" Details: {e}", file=sys.stderr)
         return False
    except subprocess.CalledProcessError as e:
        print(f"Error executing service command {' '.join(command_args)} (Exit Code {e.returncode}).", file=sys.stderr)
        if e.stdout:
            print("Subprocess STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("Subprocess STDERR:")
            print(e.stderr)
        return False
    except Exception as e:
        print(f"An unexpected error occurred running service command: {e}", file=sys.stderr)
        return False

# --- Add cleanup helpers ---
def _run_powershell_cleanup_command(command):
    """Executes a PowerShell command specifically for cleanup, ignoring most errors."""
    if platform.system() != "Windows": return True # Skip on non-windows
    print(f"Executing PowerShell Cleanup: {command}")
    try:
        # Use check=False, don't capture output unless needed for debug
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            check=False, # Don't throw error if command fails (e.g., no tasks found)
            stdout=subprocess.DEVNULL, # Suppress stdout
            stderr=subprocess.DEVNULL  # Suppress stderr
        )
        return True # Assume success for cleanup flow
    except Exception as e:
        print(f"Warning: PowerShell cleanup command failed: {e}", file=sys.stderr)
        return False # Indicate potential issue

def _cleanup_scheduled_tasks():
    """Removes all OOTB user logon scheduled tasks."""
    print("Attempting to remove any existing OOTB user logon scheduled tasks...")
    # Use -like operator and wildcard
    # Use try-catch within PowerShell for robustness
    command = f"""
    $tasks = Get-ScheduledTask | Where-Object {{ $_.TaskName -like '{_TASK_NAME_PREFIX}*' }}
    if ($tasks) {{
        Write-Host "Found $($tasks.Count) OOTB logon tasks to remove."
        $tasks | Unregister-ScheduledTask -Confirm:$false -ErrorAction SilentlyContinue
        Write-Host "OOTB logon task removal attempted."
    }} else {{
        Write-Host "No OOTB logon tasks found to remove."
    }}
    """
    _run_powershell_cleanup_command(command)
# --- End cleanup helpers ---

def install_and_start():
    """Installs and starts the Guard Service."""
    print(f"Attempting to install service: '{_SERVICE_NAME}' ('{_SERVICE_DISPLAY_NAME}')")
    # Call 'install' command first.
    # We pass check_errors=True to stop if installation fails fundamentally.
    install_success = run_service_command(['--startup', 'auto', 'install'], check_errors=True)

    if install_success:
        # Note: Even if install_success is True, pywin32 might have printed internal errors
        # like 'service already installed'. We proceed to start anyway in that case.
        print(f"\nInstallation command finished. Attempting to start service: '{_SERVICE_NAME}' (waiting a few seconds first)")
        time.sleep(3) # Give SCM time to register the install/update
        start_success = run_service_command(['start'], check_errors=True)

        if start_success:
            # Similar caveat: start might succeed according to subprocess, but pywin32 could print internal errors.
            print(f"\nService '{_SERVICE_NAME}' install command executed and start command executed.")
            print(f"Please verify service status in 'services.msc' and check logs.")
        else:
             # This path is taken if run_service_command returned False (subprocess error occurred)
             print(f"\nService '{_SERVICE_NAME}' installed/updated but the 'start' command failed with an error.", file=sys.stderr)
             print(f" Check output above, service logs ('C:\ProgramData\OOTBGuardService\guard_post_mode.log'), or Windows Event Viewer.", file=sys.stderr)
    else:
        # This path is taken if the initial 'install' command failed critically (subprocess error)
        print(f"\nService '{_SERVICE_NAME}' installation failed critically. See errors above.", file=sys.stderr)


def stop_and_remove():
    """Stops and removes the Guard Service and associated scheduled tasks."""
    print(f"Attempting to stop service: '{_SERVICE_NAME}' (will ignore errors if not running)")
    # Run stop first, ignore errors (check_errors=False)
    run_service_command(['stop'], check_errors=False)
    time.sleep(2) # Give service time to stop

    print(f"\nAttempting to remove service: '{_SERVICE_NAME}'")
    remove_success = run_service_command(['remove']) # Check if removal command itself failed

    # Always attempt task cleanup, even if service removal had issues
    _cleanup_scheduled_tasks()

    if remove_success:
        print(f"\nService '{_SERVICE_NAME}' stopped (if running) and removed successfully. Associated logon tasks cleanup attempted.")
    else:
        print(f"\nService '{_SERVICE_NAME}' removal command failed.", file=sys.stderr)
        # Make sure to mention cleanup was still attempted
        print(f" Associated logon tasks cleanup attempted.", file=sys.stderr)
        print(f" Ensure the service was stopped first, or check permissions.", file=sys.stderr)

if __name__ == '__main__':
     # Allow calling functions directly for testing if needed
     print("This script provides service management commands.")
     print("Use 'ootb-install-service' or 'ootb-remove-service' as Administrator.") 