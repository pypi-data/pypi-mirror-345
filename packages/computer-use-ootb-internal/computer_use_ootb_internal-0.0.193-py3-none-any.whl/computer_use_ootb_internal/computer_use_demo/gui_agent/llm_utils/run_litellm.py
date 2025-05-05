
import os
import logging
import base64
from litellm import completion

from .llm_utils import is_image_path, encode_image

    
def run_litellm(messages: list, system: str, llm: str, max_tokens=256, temperature=0):
    """
    Support message format: 
    1. [
        {
            "role": "user",
            "content": ["What’s in this image?"]
        },
        {
            "role": "user",
            "content": ["E:/Workspace/computer_use_ootb_internal/examples/init_states/amazon.png"],
        }
    ],

    2. str: "What’s in this image?"
    """   

    final_messages = [{"role": "system", "content": system}]

    # image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    if type(messages) == list:
        for item in messages:
            contents = []
            if isinstance(item, dict):
                for cnt in item["content"]:
                    if isinstance(cnt, str):
                        if is_image_path(cnt):
                            base64_image = encode_image(cnt)
                            content = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        # content = {"type": "image_url", "image_url": {"url": image_url}}
                        else:
                            content = {"type": "text", "text": cnt}
                    contents.append(content)
                    
                message = {"role": item["role"], "content": contents}
            else:  # str
                contents.append({"type": "text", "text": item})
                message = {"role": "user", "content": contents}
            
            final_messages.append(message)

    elif isinstance(messages, str):
        final_messages = [{"role": "user", "content": messages}]

    print(f"[litellm]-[{llm}] sending messages:", final_messages)
    

    response = completion(
        model = llm, 
        messages=final_messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    try:
        text = response.choices[0].message.content
        token_usage = int(response.usage['total_tokens'])
        return text, token_usage
        
    # return error message if the response is not successful
    except Exception as e:
        print(f"Error in interleaved openAI: {e}. This may due to your invalid OPENAI_API_KEY. Please check the response: {response.json()} ")
        return response.json()


if __name__ == "__main__":
    system_prompt = "You are a helpful assistant."

    # Set the API key of model provider
    os.environ["OPENAI_API_KEY"] = "sk-proj-1234567890"

    response, token_usage = run_litellm(
        messages=[
            {
                "role": "user",
                # "content": ["What’s in this image?"]
                'content': ["\nYou are using an Darwin device.\nYou are able to use a mouse and keyboard to interact with the computer based on the given task and screenshot.\nYou can only interact with the desktop GUI (no terminal or application menu access).\n\nYou may be given some history plan and actions, this is the response from the previous loop.\nYou should carefully consider your plan base on the task, screenshot, and history actions.\n\nYour available 'Next Action' only include:\n- ENTER: Press an enter key.\n- ESCAPE: Press an ESCAPE key.\n- INPUT: Input a string of text.\n- CLICK: Describe the ui element to be clicked.\n- HOVER: Describe the ui element to be hovered.\n- SCROLL: Scroll the screen, you must specify up or down.\n- PRESS: Describe the ui element to be pressed.\n\n\nOutput format:\n```json\n{\n    'Thinking': str, # describe your thoughts on how to achieve the task, choose one action from available actions at a time.\n    'Next Action': str, 'action_type, action description' | 'None' # one action at a time, describe it in short and precisely. \n}\n```\n\nOne Example:\n```json\n{  \n    'Thinking': 'I need to search and navigate to amazon.com.',\n    'Next Action': 'CLICK \'Search Google button\' <button_reference:icon_0004.png>.'\n}\n```\n\nIMPORTANT NOTES:\n0. Carefully observe the screenshot and read history actions.\n1. You should only give a single action at a time. for example, INPUT text, and ENTER can\'t be in one Next Action.\n2. Attach the text to Next Action, if there is text or any description for the button. \n3. You can provide the reference of the button, such as '<button_reference:icon_0004.png>', if you can find it in the in-context example.\n4. You should not include other actions, such as keyboard shortcuts.\n5. When the task is completed, you should say 'Next Action': 'None' in the json field.\nNOTE: Reference the following action trajectory to do the task, when user ask you to do the similar task.    \nIN-CONTEXT EXAMPLE:\n1: To enter the \'Cavern of Corrosion: Path of Providence\' dungeon and complete the \'Echo of War - Inner Beast\'s Battlefield\' for rewards, I need to click on the entrance.| icon_0003.png\n2: To access the dungeon or related menu, I need to click on the icon_0004 icon.| icon_0004.png\n3: To scroll down the list of available dungeons or materials, I need to use the \'Alt - MouseWheelDown\' shortcut.\n4: The user likely intended to scroll down the list of options or navigate through the interface using the mouse wheel down.\n5: To locate the \'Echo of War - Inner Beast\'s Battlefield\' dungeon, I need to scroll down the list.\n6: To view more options or details in the list, the user needs to scroll down.\n7: To proceed with the \'Echo of War - Inner Beast\'s Battlefield\' dungeon, I need to select the 'Echo of War' section.\n8: To view and select the \'Echo of War - Inner Beast\'s Battlefield\' dungeon, I need to click on the 'Echo of War' section.\n9: To complete the dungeon and receive rewards, I need to teleport to the \'Inner Beast\'s Battlefield\'.| icon_0016.png\n10: To access the \'Echo of War - Inner Beast\'s Battlefield\' dungeon, I need to click the \'Teleport\' button.| icon_0017.png\n11: To start the dungeon and receive the rewards, I need to click the \'Challenge\' button.| icon_0018.png\n12: To start the \'Echo of War - Inner Beast\'s Battlefield\' dungeon and receive the rewards, I need to click the \'Challenge\' button.| icon_0019.png\n13: To interact with or select a specific character or option, I need to click on the designated area.\n14: To interact with a specific UI element or character, I need to use \'Alt - LClick\' at the given coordinates.\n15: To begin the \'Echo of War - Inner Beast\'s Battlefield\' dungeon, I need to click the 'Start Challenge' button.| icon_0022.png\n16: To begin the dungeon and complete the task to receive rewards, I need to click the \'Start Challenge\' button.| icon_0023.png\n17: To proceed with the game or adjust settings, I need to click on the UI control.\n18: To leave the completed dungeon and return to the main game area, I need to click the \'Exit\' button.| icon_0025.png\n"]
            },
            {
                "role": "user",
                "content": ["/Users/yyyang/showlab/code/ootb_internal/computer_use_ootb_internal/output.png"],
            }
        ],
        system=system_prompt,
        llm="gpt-4o-mini",
    )

    print(response, token_usage)