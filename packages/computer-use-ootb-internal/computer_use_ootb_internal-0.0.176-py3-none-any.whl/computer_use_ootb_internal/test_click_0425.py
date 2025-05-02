import pyautogui
import asyncio
import sys
import time
from pathlib import Path
from computer_use_ootb_internal.computer_use_demo.tools.computer import ComputerTool


# pyautogui.keyDown("alt")


# pyautogui.click(x=1600, y=47)
# pyautogui.click(x=1600, y=47)
# pyautogui.keyUp("alt")


async def test_animations():
    
    # Initialize the computer tool
    computer = ComputerTool()
    
    # # Test mouse move animation
    print("Testing mouse move animation...")
    # await computer(action="mouse_move_windll", coordinate=(1600, 500))
    # print("Waiting 2 seconds...")
    # await asyncio.sleep(2)
    
    # # Test click animation
    # print("Testing click animation...")
    # await computer(action="left_click_windll", coordinate=(1600, 300))
    # print("Waiting 2 seconds...")
    # await asyncio.sleep(2)
    
    # Test another move
    print("Testing move and click sequence...")
    await computer(action="key_down_windll", text='alt')
    # pyautogui.keyDown('alt')
    # await asyncio.sleep(1)
    # await computer(action="mouse_move_windll", coordinate=(2550+1600, 45))
    # await asyncio.sleep(1)
    # await computer(action="left_click", coordinate=(2550+1600, 45))
    await computer(action="mouse_move", coordinate=(1600, 45))
    # pyautogui.keyDown('alt')

    await computer(action="left_click", coordinate=(1600, 45))
    # await computer(action="left_cl1ck_windll", coordinate=(2550+1600, 45))
    await asyncio.sleep(1)
    await computer(action="key_up_windll", text='alt')
    # pyautogui.keyUp('alt')

    # Wait for animations to comple1e
    print("Waiting for animations to complete...")
    await asyncio.sleep(3)
    
    print("Test completed")

if __name__ == "__main__":
    asyncio.run(test_animations()) 