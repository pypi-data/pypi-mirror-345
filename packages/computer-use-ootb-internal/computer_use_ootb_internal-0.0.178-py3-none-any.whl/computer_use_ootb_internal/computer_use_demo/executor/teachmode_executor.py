import ast
import json
import asyncio
from typing import Any, Dict, cast, List, Union
import uuid
from anthropic.types.beta import BetaToolUseBlock
from computer_use_ootb_internal.computer_use_demo.tools import ComputerTool, ToolCollection
from computer_use_ootb_internal.computer_use_demo.tools.base import ToolResult, ToolError


class TeachmodeExecutor:
    def __init__(
        self, 
        selected_screen: int = 0,
        full_screen_game_mode: int = 0,  # 0: disabled, 1: starrail, 2: starrail browser
    ):
        self.selected_screen = selected_screen
        self.screen_bbox = self._get_screen_resolution()
        print("Screen BBox:", self.screen_bbox)
        
        self.tool_collection = ToolCollection(
            ComputerTool(selected_screen=selected_screen, is_scaling=False)
        )
        
        self.supported_action_type={
            # "showui_action": "anthropic_tool_action"
            "CLICK": 'key',  # TBD
            "RIGHT_CLICK": 'key',  # TBD
            "INPUT": "key",
            "MOVE": "key",
            "HOVER": "key",
            "ENTER": "key",  # TBD
            "ESC": "key",
            "ESCAPE": "key",
            "PRESS":  "key",
            "KEY": "key",
            "HOTKEY": "key",
            "DRAG": "key",
            "SCROLL": "key",
            "DOUBLE_CLICK": "key",
            "TRIPLE_CLICK": "key",
            "WAIT": "key",
        }

        self.full_screen_game_mode = full_screen_game_mode



    def __call__(self, response: str):
        
        # response is expected to be:
        # {'content': "{'action': 'CLICK', 'value': None, 'position': [0.83, 0.15]}, ...", 'role': 'assistant'}, 
        
        # str -> dict
        action_dict = self._format_actor_output(response)  
        
        actions = action_dict["content"]
        
        # Parse the actions from actor
        action_list = self._parse_actor_output(actions)

        if self.full_screen_game_mode == 1:
            print("Adding StarRail Alt Actions")
            action_list = self._reformat_starrail_scrolls(action_list)
            action_list = self._add_starrail_alt_actions(action_list)

        elif self.full_screen_game_mode == 2:
            print("Converting StarRail Browser Actions")
            action_list = self._reformat_starrail_browser_actions(action_list)
            action_list = self._add_starrail_browser_alt_actions(action_list)

        print("Parsed Action List:", action_list)

        if action_list is not None and len(action_list) > 0:
                    
            for action in action_list:  
                
                # self.output_callback(f"{colorful_text_showui}:\n{action}", sender="bot")
                print("Converted Action:", action)
                
                sim_content_block = BetaToolUseBlock(
                    id=f'toolu_{uuid.uuid4()}',
                    input={'action': action["action"], 'text': action["text"], 'coordinate': action["coordinate"]},
                    name='computer',
                    type='tool_use'
                )

                # Run the asynchronous tool execution in a synchronous context
                tool_result = asyncio.run(
                    self.tool_collection.run(
                        name=sim_content_block.name,
                        tool_input=cast(dict[str, Any], sim_content_block.input),
                    ))
                
                if isinstance(tool_result, ToolResult):
                    print(f"[teachmode_executor] tool_result: {tool_result}")
                    tool_result_message = {"role": "assistant", "content": tool_result.output, "type": tool_result.type, "action_type": tool_result.action_base_type}
                    yield tool_result_message

                elif isinstance(tool_result, ToolError):
                    print(f"[teachmode_executor] tool_error: {tool_result}")
                    tool_result_message = {"role": "assistant", "content": tool_result.output, "type": "error", "action_type": ""}
                    yield tool_result_message
              
            return tool_result_message
        
    
    def _format_actor_output(self, action_output: str|dict) -> Dict[str, Any]:
        if type(action_output) == dict:
            return action_output
        else:
            try:
                action_output.replace("'", "\"")
                action_dict = ast.literal_eval(action_output)
                return action_dict
            except Exception as e:
                print(f"Error parsing action output: {e}")
                return None
    
    def _parse_actor_output(self, action_item: str | dict) -> Union[List[Dict[str, Any]], None]:
        try:
            # refine key: value pairs, mapping to the Anthropic's format
            refined_output = []
            
            if type(action_item) == str:
                action_item = ast.literal_eval(action_item)

            print("[_parse_actor_output] Action Item:", action_item)
            
            # sometime showui returns lower case action names
            action_item["action"] = action_item["action"].upper()
            
            if action_item["action"] not in self.supported_action_type:
                raise ValueError(f"Action {action_item['action']} not supported. Check the output from Actor: {action_item}")
                # continue
            
            elif action_item["action"] == "CLICK":  # 1. click -> mouse_move + left_click
                x, y = action_item["position"]
                action_item["position"] = (int(x), int(y))
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": tuple(action_item["position"])})
                refined_output.append({"action": "left_click", "text": None, "coordinate": tuple(action_item["position"])})
            
            elif action_item["action"] == "RIGHT_CLICK":  # 1. click -> mouse_move + left_click
                x, y = action_item["position"]
                action_item["position"] = (int(x), int(y))
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": tuple(action_item["position"])})
                refined_output.append({"action": "right_click", "text": None, "coordinate": tuple(action_item["position"])})

            elif action_item["action"] == "INPUT":  # 2. input -> type
                if "text" in action_item:
                    refined_output.append({"action": "type", "text": action_item["text"], "coordinate": None})
                elif "value" in action_item:
                    refined_output.append({"action": "type", "text": action_item["value"], "coordinate": None})
                else:
                    raise ValueError(f"Input action {action_item['action']} does not contain 'text' or 'value'.")
            
            elif action_item["action"] in ["ENTER", "RETURN"] \
                or (action_item["action"] == "KEY" and action_item["value"] in ["ENTER", "RETURN"]):  # 3. enter -> key, enter
                refined_output.append({"action": "key", "text": "Enter", "coordinate": None})
            
            elif action_item["action"] in ["ESCAPE", "ESC"] \
                or (action_item["action"] == "KEY" and action_item["value"] in ["ESC", "ESCAPE"]):  # 4. enter -> key, enter
                refined_output.append({"action": "key", "text": "Escape", "coordinate": None})
                
            elif action_item["action"] == "HOVER" or action_item["action"] == "MOVE":  # 5. hover -> mouse_move
                x, y = action_item["position"]
                # action_item["position"] = (int(x * (self.screen_bbox[2] - self.screen_bbox[0])),
                #                         int(y * (self.screen_bbox[3] - self.screen_bbox[1])))
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": tuple(action_item["position"])})
                
            elif action_item["action"] == "SCROLL":  # 6. scroll -> key: pagedown
                if action_item["value"] == "up":
                    # refined_output.append({"action": "key", "text": "pageup", "coordinate": None})
                    refined_output.append({"action": "scroll_up", "text": None, "coordinate": None})
                elif action_item["value"] == "down":
                    # refined_output.append({"action": "key", "text": "pagedown", "coordinate": None})
                    refined_output.append({"action": "scroll_down", "text": None, "coordinate": None})
                else:
                    raise ValueError(f"Scroll direction {action_item['value']} not supported.")

            elif action_item["action"] == "PRESS":  # 7. press
                x, y = action_item["position"]
                # action_item["position"] = (int(x * (self.screen_bbox[2] - self.screen_bbox[0])),
                #                         int(y * (self.screen_bbox[3] - self.screen_bbox[1])))
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": tuple(action_item["position"])})
                refined_output.append({"action": "left_press", "text": None, "coordinate": None})

            elif action_item["action"] in ["HOTKEY", "KEY"]:  # 8. hotkey
                refined_output.append({"action": "key", "text": action_item["value"], "coordinate": None})

            elif action_item["action"] == "DRAG":  # 9. drag
                x1, y1 = action_item["value"]
                x2, y2 = action_item["position"]
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": (x1, y1)})
                refined_output.append({"action": "left_click_drag", "text": None, "coordinate": (x2, y2)})

            elif action_item["action"] == "DOUBLE_CLICK":  # 10. double click
                x, y = action_item["position"]
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": (x, y)})
                refined_output.append({"action": "double_click", "text": None, "coordinate": None})
            
            elif action_item["action"] == "TRIPLE_CLICK":  # 11. triple click
                x, y = action_item["position"]
                refined_output.append({"action": "mouse_move", "text": None, "coordinate": (x, y)})
                refined_output.append({"action": "triple_click", "text": None, "coordinate": None})

            elif action_item["action"] == "WAIT":  # 11. wait
                refined_output.append({"action": "wait", "text": None, "coordinate": None})

            return refined_output

        except Exception as e:
            print(f"Error {e} in parsing output: {action_item}")
            # import pdb; pdb.set_trace()
            return None


    def _reformat_starrail_scrolls(self, action_list: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        converted_action_list = []
        for action in action_list:
            if action["action"] == "scroll_down":
                converted_action_list.append({"action": "sr_scroll_down", "text": None, "coordinate": None})
            elif action["action"] == "scroll_up":
                converted_action_list.append({"action": "sr_scroll_up", "text": None, "coordinate": None})
            else:
                converted_action_list.append(action)
        return converted_action_list
        
    def _add_starrail_alt_actions(self, action_list: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        parsed_action_list = []
        for action in action_list:
            if action["action"] in ["left_click", "mouse_move"]:
                parsed_action_list.append({"action": "key_down", "text": "alt", "coordinate": None})
                parsed_action_list.append(action)
                parsed_action_list.append({"action": "key_up", "text": "alt", "coordinate": None})
            else:
                parsed_action_list.append(action)
        return parsed_action_list

    def _reformat_starrail_browser_actions(self, action_list: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        converted_action_list = []
        for action in action_list:
            if action["action"] in ["left_click", "mouse_move", "key_down", "key_up"]:  # TODO: "right_click"
                action["action"] = f"{action['action']}_windll"
                converted_action_list.append(action)
            elif action["action"] == "scroll_down":
                converted_action_list.append({"action": "sr_scroll_down", "text": None, "coordinate": None})
            elif action["action"] == "scroll_up":
                converted_action_list.append({"action": "sr_scroll_up", "text": None, "coordinate": None})
            else:
                converted_action_list.append(action)
        return converted_action_list

    def _add_starrail_browser_alt_actions(self, action_list: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        parsed_action_list = []

        for action in action_list:
            if action["action"] in ["left_click", "mouse_move", "left_click_windll", "mouse_move_windll"]:
                parsed_action_list.append({"action": "key_down_windll", "text": "alt", "coordinate": None})
                parsed_action_list.append(action)
                parsed_action_list.append({"action": "key_up_windll", "text": "alt", "coordinate": None})
            else:
                parsed_action_list.append(action)

        return parsed_action_list


    def _get_screen_resolution(self):
        from screeninfo import get_monitors
        import platform
        if platform.system() == "Darwin":
            import Quartz  # uncomment this line if you are on macOS
        import subprocess
            
        # Detect platform
        system = platform.system()

        if system == "Windows":
            # Windows: Use screeninfo to get monitor details
            screens = get_monitors()

            # Sort screens by x position to arrange from left to right
            sorted_screens = sorted(screens, key=lambda s: s.x)

            if self.selected_screen < 0 or self.selected_screen >= len(screens):
                raise IndexError("Invalid screen index.")

            screen = sorted_screens[self.selected_screen]
            bbox = (screen.x, screen.y, screen.x + screen.width, screen.y + screen.height)

        elif system == "Darwin":  # macOS
            # macOS: Use Quartz to get monitor details
            max_displays = 32  # Maximum number of displays to handle
            active_displays = Quartz.CGGetActiveDisplayList(max_displays, None, None)[1]

            # Get the display bounds (resolution) for each active display
            screens = []
            for display_id in active_displays:
                bounds = Quartz.CGDisplayBounds(display_id)
                screens.append({
                    'id': display_id,
                    'x': int(bounds.origin.x),
                    'y': int(bounds.origin.y),
                    'width': int(bounds.size.width),
                    'height': int(bounds.size.height),
                    'is_primary': Quartz.CGDisplayIsMain(display_id)  # Check if this is the primary display
                })

            # Sort screens by x position to arrange from left to right
            sorted_screens = sorted(screens, key=lambda s: s['x'])

            if self.selected_screen < 0 or self.selected_screen >= len(screens):
                raise IndexError("Invalid screen index.")

            screen = sorted_screens[self.selected_screen]
            bbox = (screen['x'], screen['y'], screen['x'] + screen['width'], screen['y'] + screen['height'])

        else:  # Linux or other OS
            cmd = "xrandr | grep ' primary' | awk '{print $4}'"
            try:
                output = subprocess.check_output(cmd, shell=True).decode()
                resolution = output.strip().split()[0]
                width, height = map(int, resolution.split('x'))
                bbox = (0, 0, width, height)  # Assuming single primary screen for simplicity
            except subprocess.CalledProcessError:
                raise RuntimeError("Failed to get screen resolution on Linux.")
        
        return bbox


