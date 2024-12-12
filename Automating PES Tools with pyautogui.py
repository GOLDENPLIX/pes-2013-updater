import pyautogui
import time

def automate_tool(tool_path, steps):
    # Launch the tool
    os.startfile(tool_path)
    time.sleep(5)  # Wait for the tool to load

    for step in steps:
        pyautogui.click(step['x'], step['y'])
        time.sleep(step.get('wait', 1))

    print("Tool automation complete.")
