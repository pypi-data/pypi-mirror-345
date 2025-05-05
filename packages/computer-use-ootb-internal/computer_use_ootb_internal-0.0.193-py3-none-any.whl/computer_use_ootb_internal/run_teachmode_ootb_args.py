import argparse
import time
import json
import platform
import uuid
import base64
import datetime
from datetime import datetime, timedelta, timezone

from computer_use_ootb_internal.computer_use_demo.executor.teachmode_executor import TeachmodeExecutor
from computer_use_ootb_internal.computer_use_demo.gui_agent.llm_utils.llm_utils import is_image_path
from computer_use_ootb_internal.computer_use_demo.gui_agent.gui_parser.simple_parser.utils import get_screen_resize_factor
from computer_use_ootb_internal.computer_use_demo.tools.aws_request import send_request_to_server
from computer_use_ootb_internal.computer_use_demo.gui_agent.gui_parser.uia_tools.screenshot_service import get_screenshot_external_cmd


utc_plus_8 = timezone(timedelta(hours=8))


def simple_teachmode_sampling_loop(
    model: str,
    task: str,
    api_keys: dict = None,
    action_history: list[dict] = None,
    selected_screen: int = 0,
    user_id: str = None,
    trace_id: str = None,
    server_url: str = "http://localhost:5000/generate_action",
    max_steps: int = 20,
    full_screen_game_mode: int = 0,  # 0: disabled, 1: starrail, 2: starrail browser
):
    """
    Synchronous sampling loop for assistant/tool interactions in 'teach mode'.
    """
    # Initialize action_history if it's None
    if action_history is None:
        action_history = []

    # if platform.system() != "Windows":
    #     raise ValueError("Teach mode is only supported on Windows.")

    # # Set StarRail mode based on input parameter
    # # 0: disabled, 1: starrail, 2: starrail browser
    # full_screen_game_mode = 0 
    
    # # TODO: set full_screen_game_mode adaptively
    # if "star_rail" in user_id or "star_rail" in user_id:
    #     full_screen_game_mode = 1
    
    # if "star_rail_dev" in trace_id or "star_rail_dev" in user_id or "hero_case" in user_id or "official" in user_id:
    #     full_screen_game_mode = 2

    print(f"Full Screen Game Mode: {full_screen_game_mode}")
    executor = TeachmodeExecutor(
        selected_screen=selected_screen,
        full_screen_game_mode=full_screen_game_mode,
    )

    timestamp = datetime.now(utc_plus_8).strftime("%m%d-%H%M%S")

    step_count = 1
    unique_task_id = f"{timestamp}_uid_{user_id}_tid_{trace_id}_{str(uuid.uuid4())[:6]}"

    print("[simple_teachmode_sampling_loop] starting task: ", task)
    print(f"[simple_teachmode_sampling_loop] unique_task_id: {unique_task_id}")


    while step_count < max_steps:
        
        print(f"step_count: {step_count}")

        # Pause briefly so we don't spam screenshots
        time.sleep(1)

        uia_meta, sc_path = get_screenshot_external_cmd(
            selected_screen=selected_screen,
            capture_uia_data=full_screen_game_mode==0
        )
        
        # yield {"role": "assistant", "content": "screenshot", "type": "action", "action_type": "screenshot"}

        if is_image_path(sc_path):
            # yield {"role": "assistant", "content": sc_path, "type": "image", "action_type": "screenshot"} 
            with open(sc_path, "rb") as image_file:
                sc_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            yield {"role": "assistant", "content": sc_base64, "type": "image_base64", "action_type": "screenshot"} 

        payload = {
            "task_id": unique_task_id,
            "uia_data": uia_meta,
            "screenshot_path": sc_path,
            "query": task,
            "action_history": action_history,
            "mode": "teach",
            "user_id": user_id,
            "trace_id": trace_id,
            "scale_factor": get_screen_resize_factor(),
            "os_name": platform.system(),
            "api_keys": api_keys,
        }

        # Send request to Marbot Run server
        infer_server_response = send_request_to_server(payload, server_url)

        # infer_server_response = {
        #     'status': 'success',
        #     'generated_plan': plan_details,
        #     'generated_action': action,
        #     'todo_md': todo_md_content,
        #     'milestones': milestones,
        #     'current_step': current_step,
        # }


        if infer_server_response is None:
            print("No response from Marbot Run server. Exiting.")
            yield {"role": "assistant", "content": "No response from Marbot Run server. Exiting.", "type": "error"}
            action_history = []
            break

        try:
            step_plan = infer_server_response["generated_plan"]
            step_plan_observation = step_plan["observation"]
            step_plan_reasoning = step_plan["reasoning"]
            step_plan_info = step_plan["step_info"]
            step_action = infer_server_response["generated_action"]["content"]
            step_traj_idx = infer_server_response["current_traj_step"]

            # chat_visable_content = f"{step_plan_observation}{step_plan_reasoning}"

        except Exception as e:
            print("Error parsing generated_action content:", e)
            yield {"role": "assistant", "content": "Error parsing response from Marbot Run server. Exiting.", "type": "error"}
            break

        yield {"role": "assistant", "content": step_plan_observation, "type": "text"}
        yield {"role": "assistant", "content": step_plan_reasoning, "type": "text"}

        if step_action.get("action") == "STOP":
            final_sc, final_sc_path = get_screenshot_external_cmd(selected_screen=selected_screen)

            with open(final_sc_path, "rb") as image_file:
                final_sc_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            yield {"role": "assistant", "content": "Task completed. Final screenshot:", "type": "text"}
            yield {"role": "assistant", "content": final_sc_base64, "type": "image_base64", "action_type": "screenshot"} 

            # reset action history
            action_history = []  
            break

        action_history.append(f"Executing guidance trajectory step [{step_traj_idx}]: {{Plan: {step_plan_info}, Action: {step_action}}}\n")

        for exec_message in executor({"role": "assistant", "content": step_action}):
            yield exec_message

        step_count += 1
    
    # reset action history
    action_history = []



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a synchronous sampling loop for assistant/tool interactions in teach-mode."
    )
    parser.add_argument(
        "--model",
        default="teach-mode",
        help="The model to use",
    )
    parser.add_argument(
        "--task",
        default="Click on the Google Chorme icon",
        help="The task to be completed by the assistant (e.g., 'Complete some data extraction.').",
    )
    parser.add_argument(
        "--selected_screen",
        type=int,
        default=0,
        help="Index of the screen to capture (default=0).",
    )
    parser.add_argument(
        "--user_id",
        default="star_rail",
        help="User ID for the session (default='liziqi').",
    )
    parser.add_argument(
        "--trace_id",
        default="ONG_JING_JIE_007-0213_0",
        help="Trace ID for the session (default='default_trace').",
    )
    parser.add_argument(
        "--api_key_file",
        default="api_key.json",
        help="Path to the JSON file containing API keys (default='api_key.json').",
    )
    parser.add_argument(
        "--max_steps",
        type=int,
        default=20,
        help="The maximum number of steps to take.",
    )
    parser.add_argument(
        "--full_screen_game_mode",
        type=int,
        default=0,
        help="Full screen game mode (0: disabled, 1: starrail, 2: starrail browser)",
    )

    args = parser.parse_args()

    # # Load API keys
    # with open(args.api_key_file, "r") as file:
    #     api_keys = json.load(file)
    api_keys = None

    print(f"Starting task: {args.task}")

    # Execute the sampling loop
    sampling_loop = simple_teachmode_sampling_loop(
        model=args.model,
        task=args.task,
        selected_screen=args.selected_screen,
        user_id=args.user_id,
        trace_id=args.trace_id,
        api_keys=api_keys,
        max_steps=args.max_steps,
        full_screen_game_mode=args.full_screen_game_mode,
    )

    # # Print each step result
    for step in sampling_loop:
        print(step)
        time.sleep(1)

    print(f"Task '{args.task}' completed. Thanks for using Teachmode-OOTB.")
