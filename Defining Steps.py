steps = [
    {'x': 500, 'y': 400, 'wait': 2},  # Click "Open"
    {'x': 600, 'y': 450, 'wait': 3},  # Select file
    {'x': 700, 'y': 500, 'wait': 1},  # Click "Save"
]
automate_tool('path_to_editor.exe', steps)
