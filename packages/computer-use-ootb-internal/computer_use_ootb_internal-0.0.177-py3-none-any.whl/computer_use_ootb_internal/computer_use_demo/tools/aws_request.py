import requests
import json
import base64

def convert_screenshot_to_base64(screenshot_path):
    """
    Converts a screenshot file to a Base64-encoded string.

    Args:
        screenshot_path (str): Path to the screenshot file.

    Returns:
        str: Base64-encoded string of the image.
    """
    try:
        with open(screenshot_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        return base64_image
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {screenshot_path} was not found.")
    except Exception as e:
        raise RuntimeError(f"An error occurred while converting the image: {e}")


def send_request_to_server(payload, url="http://ec2-44-234-43-86.us-west-2.compute.amazonaws.com/generate_action"):
    # Server URL
    url = "http://ec2-44-234-43-86.us-west-2.compute.amazonaws.com/generate_action"
    
    payload["screenshot"] = convert_screenshot_to_base64(payload["screenshot_path"])
    del payload["screenshot_path"]

    # Set headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # print("sending payload", [f"{k}: {str(v)[:200]}" for k, v in payload.items() if k != "screenshot"])

    try:
        # Send POST request
        response = requests.post(url, json=payload, headers=headers)
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        print("Status:", result["status"])
        # print("\nParsed GUI:", json.dumps(result["parsed_gui"], indent=2))
        print("\nGenerated Action:", json.dumps(result["generated_action"], indent=2))
        
        return result

    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        if hasattr(e.response, 'text'):
            print(f"Server response: {e.response.text}")
        return None

if __name__ == "__main__":
    
    # Example input data
    payload = {
        "uia_data": None,
        "screenshot_path": "/Users/yyyang/showlab/code/ootb_internal/computer_use_ootb_internal/honkai-star-rail-menu-resized.jpg",
        "query": "Help me to complete the mission 'Buds of Memories' in Star Rail",
        "action_history": "Open the menu interface.",
        "mode": "teach",
        
        # Optional parameters
        "user_id": "star_rail",
        "trace_id": "default_trace",
        "scale_factor": "1.0x",
        "os_name": "Windows",
        "date_time": "2024-01-01",
        "llm_model": "gpt-4"
    }
    send_request_to_server(payload) 
