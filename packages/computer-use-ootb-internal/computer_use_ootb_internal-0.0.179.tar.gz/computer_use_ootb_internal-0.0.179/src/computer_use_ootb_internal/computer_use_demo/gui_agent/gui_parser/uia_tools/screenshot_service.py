import subprocess
import json
import os
import sys
from importlib import resources, util
from pathlib import Path

def get_screenshot_external_cmd(selected_screen=0, capture_uia_data=True, python_exec="python"):
    """
    Spawns a new Python process that runs 'screenshot_cli.py' in a new CMD window.
    Captures JSON from stdout and returns it.
    """
    try:
        # First locate the screenshot_cli module
        module_name = 'computer_use_ootb_internal.computer_use_demo.gui_agent.gui_parser.uia_tools.screenshot_cli'
        spec = util.find_spec(module_name)

        if spec is None or spec.origin is None:
            raise ImportError(f"Could not find module: {module_name}")
        script_path = Path(spec.origin)
        
        # Get the site-packages directory
        site_packages = Path(script_path).parents[5]
        
        # Find the actual package directory
        package_path = site_packages / 'computer_use_ootb_internal'
        
        if not package_path.exists():
            raise ImportError(f"Package directory not found at {package_path}")
            
        current_dir = package_path
        
    except Exception as e:
        print(f"Error finding paths: {e}")
        print(f"sys.path: {sys.path}")
        raise

    # print(f"current_dir: {current_dir}")
    # print(f"script_path: {script_path}")
    
    # Build and run the command
    cmd = [python_exec, str(script_path),
            "--screen", str(selected_screen),
            "--uia", str(capture_uia_data)]
    
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        cwd=str(current_dir)
    )
    
    # import pdb; pdb.set_trace()

    # Check for errors
    if result.returncode != 0:
        print(f"Command output: {result.stdout}")
        print(f"Command error: {result.stderr}")
        raise RuntimeError(f"Screenshot process failed with return code {result.returncode}")

    # Parse JSON from stdout
    stdout_str = result.stdout.strip()
    try:
        data = json.loads(stdout_str)
        meta_data = data["meta_data"]
        # Convert relative screenshot path to absolute
        screenshot_path = data["screenshot_path"]
        if not os.path.isabs(screenshot_path):
            screenshot_path = os.path.abspath(os.path.join(str(current_dir), screenshot_path))
        data["screenshot_path"] = screenshot_path
    except json.JSONDecodeError as e:
        print(f"Raw output: {stdout_str}")
        raise ValueError(f"Invalid JSON returned from screenshot process") from e
    except KeyError as e:
        print(f"JSON data: {data}")
        raise ValueError(f"Missing required key in JSON response: {e}") from e
    
    return meta_data, screenshot_path