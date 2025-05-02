import argparse
import time
import json
from datetime import datetime
import threading
import requests
import platform  # Add platform import
import pyautogui  # Add pyautogui import
import webbrowser # Add webbrowser import
import os # Import os for path joining
import logging # Import logging
import importlib # For dynamic imports
import pkgutil # To find modules
import sys # For logging setup
import traceback # For logging setup
from logging.handlers import RotatingFileHandler # For logging setup
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from computer_use_ootb_internal.computer_use_demo.tools.computer import get_screen_details
from computer_use_ootb_internal.run_teachmode_ootb_args import simple_teachmode_sampling_loop
from computer_use_ootb_internal.computer_use_demo.executor.teachmode_executor import TeachmodeExecutor
import uvicorn # Assuming uvicorn is used to run FastAPI
import concurrent.futures
import asyncio

# --- App Logging Setup ---
try:
    # Log to user's AppData directory for better accessibility
    log_dir_base = os.environ.get('APPDATA', os.path.expanduser('~'))
    log_dir = os.path.join(log_dir_base, 'OOTBAppLogs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'ootb_app.log')

    log_format = '%(asctime)s - %(levelname)s - %(process)d - %(threadName)s - %(message)s'
    log_level = logging.INFO # Or logging.DEBUG for more detail

    # Use rotating file handler
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2, encoding='utf-8')
    handler.setFormatter(logging.Formatter(log_format))

    # Configure root logger
    logging.basicConfig(level=log_level, handlers=[handler])

    # Add stream handler to see logs if running interactively (optional)
    # logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    logging.info("="*20 + " OOTB App Starting " + "="*20)
    logging.info(f"Running with args: {sys.argv}")
    logging.info(f"Python Executable: {sys.executable}")
    logging.info(f"Working Directory: {os.getcwd()}")
    logging.info(f"User: {os.getenv('USERNAME')}")

except Exception as log_setup_e:
    print(f"FATAL: Failed to set up logging: {log_setup_e}")
    # Fallback logging might be needed here if file logging fails

# --- End App Logging Setup ---

app = FastAPI()

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter for API endpoints
class RateLimiter:
    def __init__(self, interval_seconds=2):
        self.interval = interval_seconds
        self.last_request_time = {}
        self.lock = threading.Lock()
        
    def allow_request(self, endpoint):
        with self.lock:
            current_time = time.time()
            # Priority endpoints always allowed
            if endpoint in ["/update_params", "/update_message"]:
                return True
                
            # For other endpoints, apply rate limiting
            if endpoint not in self.last_request_time:
                self.last_request_time[endpoint] = current_time
                return True
                
            elapsed = current_time - self.last_request_time[endpoint]
            if elapsed < self.interval:
                return False
                
            self.last_request_time[endpoint] = current_time
            return True


def log_ootb_request(server_url, ootb_request_type, data):
    logging.info(f"OOTB Request: Type={ootb_request_type}, Data={data}")
    # Keep the requests post for now if it serves a specific purpose
    logging_data = {
        "type": ootb_request_type,
        "data": data,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if not server_url.endswith("/update_ootb_logging"):
        server_logging_url = server_url + "/update_ootb_logging"
    else:
        server_logging_url = server_url
    try:
        requests.post(server_logging_url, json=logging_data, timeout=5)
    except Exception as req_log_e:
        logging.warning(f"Could not log ootb request to server {server_logging_url}: {req_log_e}")


class SharedState:
    def __init__(self, args):
        self.args = args
        self.task_updated = False
        self.chatbot_messages = []
        # Store all state-related data here
        self.model = args.model
        self.task = getattr(args, 'task', "")
        self.selected_screen = args.selected_screen
        self.user_id = args.user_id
        self.trace_id = args.trace_id
        self.api_keys = args.api_keys
        self.server_url = args.server_url
        self.message_queue = []
        self.is_processing = False
        self.should_stop = False
        self.is_paused = False
        self.full_screen_game_mode = getattr(args, 'full_screen_game_mode', 0)
        # Add a new event to better control stopping
        self.stop_event = threading.Event()
        # Add a reference to the processing thread
        self.processing_thread = None
        self.max_steps = getattr(args, 'max_steps', 50)

shared_state = None
rate_limiter = RateLimiter(interval_seconds=2)

# Set up logging for this module
log = logging.getLogger(__name__)

def prepare_environment(state):
    """Dynamically loads and runs preparation logic based on software name."""
    # Determine software name from state (user_id, trace_id, or task)
    software_name = ""
    
    # Check user_id first
    user_id = getattr(state, 'user_id', '').lower()
    task = getattr(state, 'task', '').lower()
    trace_id = getattr(state, 'trace_id', '').lower()
    
    log.info(f"Checking for software in: user_id='{user_id}', trace_id='{trace_id}', task='{task}'")
    
    # Look for known software indicators
    if "star rail" in user_id or "star rail" in trace_id:
        software_name = "star rail"
    elif "powerpoint" in user_id or "powerpoint" in trace_id or "powerpoint" in task:
        software_name = "powerpoint"
    # Add more software checks here as needed
    
    # If no specific software found, check task for keywords
    if not software_name:
        log.info("No specific software detected from IDs, checking task content")
    
    if not software_name:
        log.info("No specific software preparation identified. Skipping preparation.")
        return
    
    log.info(f"Identified software for preparation: '{software_name}'")
    
    # Normalize the software name to be a valid Python module name
    # Replace spaces/hyphens with underscores, convert to lowercase
    module_name_base = software_name.replace(" ", "_").replace("-", "_").lower()
    module_to_run = f"{module_name_base}_prepare"

    log.info(f"Attempting preparation for software: '{software_name}' (Module: '{module_to_run}')")

    try:
        # Construct the full module path within the package
        prep_package = "computer_use_ootb_internal.preparation"
        full_module_path = f"{prep_package}.{module_to_run}"

        # Dynamically import the module
        # Check if module exists first using pkgutil to avoid import errors
        log.debug(f"Looking for preparation module: {full_module_path}")
        loader = pkgutil.find_loader(full_module_path)
        if loader is None:
            log.warning(f"Preparation module '{full_module_path}' not found. Skipping preparation.")
            return

        log.debug(f"Importing preparation module: {full_module_path}")
        prep_module = importlib.import_module(full_module_path)

        # Check if the module has the expected function
        if hasattr(prep_module, "run_preparation") and callable(prep_module.run_preparation):
            log.info(f"Running preparation function from {full_module_path}...")
            prep_module.run_preparation(state)
            log.info(f"Preparation function from {full_module_path} completed.")
        else:
            log.warning(f"Module {full_module_path} found, but does not have a callable 'run_preparation' function. Skipping.")

    except ModuleNotFoundError:
        log.warning(f"Preparation module '{full_module_path}' not found. Skipping preparation.")
    except Exception as e:
        log.error(f"Error during dynamic preparation loading/execution for '{module_to_run}': {e}", exc_info=True)


@app.post("/update_params")
async def update_parameters(request: Request):
    logging.info("Received request to /update_params")
    try:
        data = await request.json()
        
        if 'task' not in data:
            return JSONResponse(
                content={"status": "error", "message": "Missing required field: task"},
                status_code=400
            )
        
        # Clear message histories before updating parameters
        shared_state.message_queue.clear()
        shared_state.chatbot_messages.clear()
        logging.info("Cleared message queue and chatbot messages.")

        shared_state.args = argparse.Namespace(**data)
        shared_state.task_updated = True
        
        # Update shared state when parameters change
        shared_state.model = getattr(shared_state.args, 'model', "teach-mode-gpt-4o")
        shared_state.task = getattr(shared_state.args, 'task', "Following the instructions to complete the task.")
        shared_state.selected_screen = getattr(shared_state.args, 'selected_screen', 0)
        shared_state.user_id = getattr(shared_state.args, 'user_id', "hero_cases")
        shared_state.trace_id = getattr(shared_state.args, 'trace_id', "build_scroll_combat")
        shared_state.api_keys = getattr(shared_state.args, 'api_keys', "sk-proj-1234567890")
        shared_state.server_url = getattr(shared_state.args, 'server_url', "http://ec2-44-234-43-86.us-west-2.compute.amazonaws.com")
        shared_state.max_steps = getattr(shared_state.args, 'max_steps', 50)

        log_ootb_request(shared_state.server_url, "update_params", data)

        # Call the (now dynamic) preparation function here, after parameters are updated
        prepare_environment(shared_state)

        logging.info("Parameters updated successfully.")
        return JSONResponse(
            content={"status": "success", "message": "Parameters updated", "new_args": vars(shared_state.args)},
            status_code=200
        )
    except Exception as e:
        logging.error("Error processing /update_params:", exc_info=True)
        return JSONResponse(content={"status": "error", "message": "Internal server error"}, status_code=500)

@app.post("/update_message")
async def update_message(request: Request):
    data = await request.json()
    
    if 'message' not in data:
        return JSONResponse(
            content={"status": "error", "message": "Missing required field: message"},
            status_code=400
        )
    
    log_ootb_request(shared_state.server_url, "update_message", data)
    
    message = data['message']
    full_screen_game_mode = data.get('full_screen_game_mode', 0)  # Default to 0 if not provided
    
    # shared_state.chatbot_messages.append({"role": "user", "content": message, "type": "text"})
    shared_state.task = message
    shared_state.args.task = message
    shared_state.full_screen_game_mode = full_screen_game_mode
    
    # Reset stop event before starting
    shared_state.stop_event.clear()
    
    # Start processing if not already running
    if not shared_state.is_processing:
        # Create and store the thread
        shared_state.processing_thread = threading.Thread(target=process_input, daemon=True)
        shared_state.processing_thread.start()
    
    return JSONResponse(
        content={"status": "success", "message": "Message received", "task": shared_state.task},
        status_code=200
    )

@app.get("/get_messages")
async def get_messages(request: Request):
    # Apply rate limiting
    if not rate_limiter.allow_request(request.url.path):
        return JSONResponse(
            content={"status": "error", "message": "Rate limit exceeded. Try again after 2 seconds."},
            status_code=429
        )
    
    # log_ootb_request(shared_state.server_url, "get_messages", {})
    
    # Return all messages in the queue and clear it
    messages = shared_state.message_queue.copy()
    shared_state.message_queue = []
    
    return JSONResponse(
        content={"status": "success", "messages": messages},
        status_code=200
    )

@app.get("/get_screens")
async def get_screens(request: Request):
    # Apply rate limiting
    if not rate_limiter.allow_request(request.url.path):
        return JSONResponse(
            content={"status": "error", "message": "Rate limit exceeded. Try again after 2 seconds."},
            status_code=429
        )
    
    log_ootb_request(shared_state.server_url, "get_screens", {})
    
    screen_options, primary_index = get_screen_details()
    
    return JSONResponse(
        content={"status": "success", "screens": screen_options, "primary_index": primary_index},
        status_code=200
    )

@app.post("/stop_processing")
async def stop_processing(request: Request):
    # Apply rate limiting
    if not rate_limiter.allow_request(request.url.path):
        return JSONResponse(
            content={"status": "error", "message": "Rate limit exceeded. Try again after 2 seconds."},
            status_code=429
        )
    
    log_ootb_request(shared_state.server_url, "stop_processing", {})
    
    if shared_state.is_processing:
        # Set both flags to ensure stopping the current task
        shared_state.should_stop = True
        shared_state.stop_event.set()
        
        # Clear message histories
        shared_state.message_queue.clear()
        shared_state.chatbot_messages.clear()
        logging.info("Cleared message queue and chatbot messages during stop.")
        
        # Send an immediate message to the queue to inform the user
        stop_initiated_msg = {"role": "assistant", "content": f"Stopping task '{shared_state.task}'...", "type": "text", "action_type": ""}
        # Append the stop message AFTER clearing, so it's the only one left
        shared_state.message_queue.append(stop_initiated_msg)
        shared_state.chatbot_messages.append(stop_initiated_msg)
        
        return JSONResponse(
            content={"status": "success", "message": "Task is being stopped, server will remain available for new tasks"},
            status_code=200
        )
    else:
        # Clear message histories even if not processing, to ensure clean state
        shared_state.message_queue.clear()
        shared_state.chatbot_messages.clear()
        logging.info("Cleared message queue and chatbot messages (no active process to stop).")
        return JSONResponse(
            content={"status": "error", "message": "No active processing to stop"},
            status_code=400
        )

@app.post("/toggle_pause")
async def toggle_pause(request: Request):
    # Apply rate limiting
    if not rate_limiter.allow_request(request.url.path):
        return JSONResponse(
            content={"status": "error", "message": "Rate limit exceeded. Try again after 2 seconds."},
            status_code=429
        )
    
    log_ootb_request(shared_state.server_url, "toggle_pause", {})
    
    if not shared_state.is_processing:
        return JSONResponse(
            content={"status": "error", "message": "No active processing to pause/resume"},
            status_code=400
        )
    
    # Toggle the pause state
    shared_state.is_paused = not shared_state.is_paused
    current_state = shared_state.is_paused
    
    print(f"Toggled pause state to: {current_state}")
    
    status_message = "paused" if current_state else "resumed"
    
    # Add a message to the queue to inform the user
    if current_state:
        message = {"role": "assistant", "content": f"Task '{shared_state.task}' has been paused. Click Continue to resume.", "type": "text", "action_type": ""}
    else:
        message = {"role": "assistant", "content": f"Task '{shared_state.task}' has been resumed.", "type": "text", "action_type": ""}
    
    shared_state.chatbot_messages.append(message)
    shared_state.message_queue.append(message)
    
    return JSONResponse(
        content={
            "status": "success", 
            "message": f"Processing {status_message}",
            "is_paused": current_state
        },
        status_code=200
    )

@app.get("/status")
async def get_status(request: Request):
    # Apply rate limiting
    if not rate_limiter.allow_request(request.url.path):
        return JSONResponse(
            content={"status": "error", "message": "Rate limit exceeded. Try again after 2 seconds."},
            status_code=429
        )
    
    # log_ootb_request(shared_state.server_url, "get_status", {})
    
    print(f"Status check - Processing: {shared_state.is_processing}, Paused: {shared_state.is_paused}")
    return JSONResponse(
        content={
            "status": "success",
            "is_processing": shared_state.is_processing,
            "is_paused": shared_state.is_paused
        },
        status_code=200
    )

@app.post("/exec_computer_tool")
async def exec_computer_tool(request: Request):
    logging.info("Received request to /exec_computer_tool")
    try:
        data = await request.json()
        
        # Extract parameters from the request
        selected_screen = data.get('selected_screen', 0)
        full_screen_game_mode = data.get('full_screen_game_mode', 0)
        response = data.get('response', {})
        
        logging.info(f"Executing TeachmodeExecutor with: screen={selected_screen}, mode={full_screen_game_mode}, response={response}")
        
        # Create TeachmodeExecutor in a separate process to avoid event loop conflicts
        # Since TeachmodeExecutor uses asyncio.run() internally, we need to run it in a way
        # that doesn't conflict with FastAPI's event loop
        
        def run_executor():
            executor = TeachmodeExecutor(
                selected_screen=selected_screen,
                full_screen_game_mode=full_screen_game_mode
            )
            
            results = []
            try:
                for action_result in executor(response):
                    results.append(action_result)
            except Exception as exec_error:
                logging.error(f"Error executing action: {exec_error}", exc_info=True)
                return {"error": str(exec_error)}
            
            return results
        
        # Execute in a thread pool to avoid blocking the event loop
        with concurrent.futures.ThreadPoolExecutor() as pool:
            results = await asyncio.get_event_loop().run_in_executor(pool, run_executor)
        
        if isinstance(results, dict) and "error" in results:
            return JSONResponse(
                content={"status": "error", "message": results["error"]},
                status_code=500
            )
            
        logging.info(f"Action results: {results}")
        
        return JSONResponse(
            content={"status": "success", "results": results},
            status_code=200
        )
    except Exception as e:
        logging.error("Error processing /exec_computer_tool:", exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": f"Internal server error: {str(e)}"},
            status_code=500
        )

def process_input():
    global shared_state
    logging.info("process_input thread started.")
    shared_state.is_processing = True
    shared_state.should_stop = False
    shared_state.is_paused = False
    shared_state.stop_event.clear()  # Ensure stop event is cleared at the start
    
    print(f"start sampling loop: {shared_state.chatbot_messages}")
    print(f"shared_state.args before sampling loop: {shared_state.args}")


    try:
        # Get the generator for the sampling loop
        sampling_loop = simple_teachmode_sampling_loop(
            model=shared_state.model,
            task=shared_state.task,
            selected_screen=shared_state.selected_screen,
            user_id=shared_state.user_id,
            trace_id=shared_state.trace_id,
            api_keys=shared_state.api_keys,
            server_url=shared_state.server_url,
            full_screen_game_mode=shared_state.full_screen_game_mode,
            max_steps=shared_state.max_steps,
        )

        # Process messages from the sampling loop
        for loop_msg in sampling_loop:
            # Check stop condition more frequently
            if shared_state.should_stop or shared_state.stop_event.is_set():
                print("Processing stopped by user")
                break
                
            # Check if paused and wait while paused
            while shared_state.is_paused and not shared_state.should_stop and not shared_state.stop_event.is_set():
                print(f"Processing paused at: {time.strftime('%H:%M:%S')}")
                # Wait a short time and check stop condition regularly
                for _ in range(5):  # Check 5 times per second
                    if shared_state.should_stop or shared_state.stop_event.is_set():
                        break
                    time.sleep(0.2)
                
            # Check again after pause loop    
            if shared_state.should_stop or shared_state.stop_event.is_set():
                print("Processing stopped while paused or resuming")
                break
                
            shared_state.chatbot_messages.append(loop_msg)
            shared_state.message_queue.append(loop_msg)
            
            # Short sleep to allow stop signals to be processed
            for _ in range(5):  # Check 5 times per second
                if shared_state.should_stop or shared_state.stop_event.is_set():
                    print("Processing stopped during sleep")
                    break
                time.sleep(0.1)
                
            if shared_state.should_stop or shared_state.stop_event.is_set():
                break

    except Exception as e:
        # Handle any exceptions in the processing loop
        error_msg = f"Error during task processing: {e}"
        print(error_msg)
        error_message = {"role": "assistant", "content": error_msg, "type": "error", "action_type": ""}
        shared_state.message_queue.append(error_message)
    
    finally:
        # Handle completion or interruption
        if shared_state.should_stop or shared_state.stop_event.is_set():
            stop_msg = f"Task '{shared_state.task}' was stopped. Ready for new tasks."
            final_message = {"role": "assistant", "content": stop_msg, "type": "text", "action_type": ""}
        else:
            complete_msg = f"Task '{shared_state.task}' completed. Thanks for using Teachmode-OOTB."
            final_message = {"role": "assistant", "content": complete_msg, "type": "text", "action_type": ""}
            
        shared_state.chatbot_messages.append(final_message)
        shared_state.message_queue.append(final_message)
        
        # Reset all state flags to allow for new tasks
        shared_state.is_processing = False
        shared_state.should_stop = False
        shared_state.is_paused = False
        shared_state.stop_event.clear()
        print("Processing completed, ready for new tasks")
    logging.info("process_input thread finished.")

def main():
    # Logging is set up at the top level now
    logging.info("App main() function starting setup.")
    global app, shared_state, rate_limiter # Ensure app is global if needed by uvicorn
    parser = argparse.ArgumentParser()
    # Add arguments, but NOT host and port
    parser.add_argument("--model", type=str, default="teach-mode-gpt-4o", help="Model name")
    parser.add_argument("--task", type=str, default="Following the instructions to complete the task.", help="Initial task description")
    parser.add_argument("--selected_screen", type=int, default=0, help="Selected screen index")
    parser.add_argument("--user_id", type=str, default="hero_cases", help="User ID for the session")
    parser.add_argument("--trace_id", type=str, default="build_scroll_combat", help="Trace ID for the session")
    parser.add_argument("--api_keys", type=str, default="sk-proj-1234567890", help="API keys")
    parser.add_argument("--server_url", type=str, default="http://ec2-44-234-43-86.us-west-2.compute.amazonaws.com", help="Server URL for the session")

    args = parser.parse_args()

    # Validate args or set defaults if needed (keep these)
    if not hasattr(args, 'model'): args.model = "default_model"
    if not hasattr(args, 'task'): args.task = "default_task"
    if not hasattr(args, 'selected_screen'): args.selected_screen = 0
    if not hasattr(args, 'user_id'): args.user_id = "unknown_user"
    if not hasattr(args, 'trace_id'): args.trace_id = "unknown_trace"
    if not hasattr(args, 'api_keys'): args.api_keys = "none"
    if not hasattr(args, 'server_url'): args.server_url = "none"

    shared_state = SharedState(args)
    rate_limiter = RateLimiter(interval_seconds=2) # Re-initialize rate limiter
    logging.info(f"Shared state initialized for user: {args.user_id}")

    # --- Restore original port calculation logic --- 
    port = 7888 # Default port
    host = "0.0.0.0" # Listen on all interfaces
    
    if platform.system() == "Windows":
        try:
            username = os.environ["USERNAME"].lower()
            logging.info(f"Determining port based on Windows username: {username}")
            if username == "altair":
                port = 14000
            elif username.startswith("guest") and username[5:].isdigit():
                num = int(username[5:])
                if 1 <= num <= 10: # Assuming max 10 guests for this range
                    port = 14000 + num
                else:
                     logging.warning(f"Guest user number {num} out of range (1-10), using default port {port}.")
            else:
                logging.info(f"Username '{username}' doesn't match specific rules, using default port {port}.")
        except Exception as e:
             logging.error(f"Error determining port from username: {e}. Using default port {port}.", exc_info=True)
    else:
         logging.info(f"Not running on Windows, using default port {port}.")
    # --- End of restored port calculation --- 

    logging.info(f"Final Host={host}, Port={port}")

    try:
        logging.info(f"Starting Uvicorn server on {host}:{port}")
        # Use the calculated port and specific host
        uvicorn.run(app, host=host, port=port)
        logging.info("Uvicorn server stopped.")
    except Exception as main_e:
        logging.error("Error in main execution:", exc_info=True)
    finally:
        logging.info("App main() function finished.")

if __name__ == "__main__":
    main()

    # Test log_ootb_request
    log_ootb_request("http://ec2-44-234-43-86.us-west-2.compute.amazonaws.com", "test_request", {"message": "Test message"})