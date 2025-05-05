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


def test_pyautogui_pptdemo():

    pyautogui.click(x=617, y=535)
    time.sleep(3)

    pyautogui.moveTo(x=1216, y=706, duration=0.4)
    time.sleep(0.1)
    pyautogui.click(x=1216, y=706)
    time.sleep(0.1)
    pyautogui.moveTo(x=2992, y=673, duration=0.1)
    time.sleep(0.5)
    
    pyautogui.typewrite("Add a fasinating 'fly wheel' transition to my presentation at the slide 6. ", interval=0.03)
    time.sleep(0.5)
    pyautogui.typewrite("Preview it when you're done.", interval=0.03)
    time.sleep(2)

    pyautogui.moveTo(x=3342, y=856, duration=0.4)
    time.sleep(0.5)
    pyautogui.click(x=3342, y=856)
    
    time.sleep(6)

    pyautogui.moveTo(x=668, y=150, duration=0.4)
    time.sleep(0.1)
    pyautogui.click(x=668, y=150)
    
    time.sleep(3)
    
    pyautogui.moveTo(x=949, y=2050, duration=0.4)
    time.sleep(0.5)
    pyautogui.click(x=949, y=2050)

    pyautogui.moveTo(x=5476, y=1033)



def test_pyautogui_starrail_demo():


    pyautogui.moveTo(x=949, y=2050, duration=0.4)
    time.sleep(0.5)
    pyautogui.click(x=949, y=2050)
    

if __name__ == "__main__":
    # asyncio.run(test_animations()) w
    test_pyautogui_starrail_demo()