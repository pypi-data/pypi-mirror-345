# screenshot_cli.py
import sys
import json
import argparse

from pathlib import Path
# get root dir of ootb
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from computer_use_demo.gui_agent.gui_parser.simple_parser.gui_capture import GUICapture

def main():
    # 1) Parse command-line arguments
    parser = argparse.ArgumentParser(description='Screenshot utility with UIA data capture')
    parser.add_argument('--screen', type=int, default=0, help='Screen number to capture (default: 0)')
    parser.add_argument('--uia', type=lambda x: x.lower() == 'true', default=True, 
                        help='Capture UIA data (default: True)')
    
    args = parser.parse_args()
    selected_screen = args.screen
    capture_uia_data = args.uia

    # 2) Perform the screenshot capture
    # **Important**:
    #  make sure nothing is printed to stdout in GUICapture.capture()
    #  since we capture the stdout in the main process
    gui = GUICapture(selected_screen=selected_screen)
    meta_data, screenshot_path = gui.capture(capture_uia_data=capture_uia_data)

    # 3) Print JSON to stdout
    output = {
        "meta_data": meta_data,
        "screenshot_path": screenshot_path
    }
    print(json.dumps(output))  # critical: print to stdout

if __name__ == "__main__":
    main()
