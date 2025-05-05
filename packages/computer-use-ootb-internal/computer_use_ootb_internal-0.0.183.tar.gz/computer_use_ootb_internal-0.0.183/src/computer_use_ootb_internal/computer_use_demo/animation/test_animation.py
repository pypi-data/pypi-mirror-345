"""
Test script to verify cursor animation is working
"""
import asyncio
import sys
import time
from pathlib import Path
from computer_use_ootb_internal.computer_use_demo.tools.computer import ComputerTool

async def test_animations():
    
    # Initialize the computer tool
    computer = ComputerTool()
    
    # Test mouse move animation
    print("Testing mouse move animation...")
    await computer(action="mouse_move_windll", coordinate=(500, 500))
    print("Waiting 2 seconds...")
    await asyncio.sleep(2)
    
    # Test click animation
    print("Testing click animation...")
    await computer(action="left_click_windll", coordinate=(700, 300))
    print("Waiting 2 seconds...")
    await asyncio.sleep(2)
    
    # Test another move
    print("Testing move and click sequence...")
    await computer(action="mouse_move_windll", coordinate=(300, 300))
    await asyncio.sleep(1)
    await computer(action="left_click_windll", coordinate=(300, 300))
    
    # Wait for animations to complete
    print("Waiting for animations to complete...")
    await asyncio.sleep(3)
    
    print("Test completed")

if __name__ == "__main__":
    asyncio.run(test_animations()) 