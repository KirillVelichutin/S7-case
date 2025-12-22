import pyautogui
import time
import pyperclip

import re
import json
import random

def extract_json_from_text(text):
    # Pattern to match JSON objects (handles nested structures)
    json_pattern = r'\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}'
    
    json_objects = []
    matches = re.finditer(json_pattern, text)
    
    for match in matches:
        try:
            json_obj = json.loads(match.group())
            json_objects.append(json_obj)
        except json.JSONDecodeError:
            # If it's not valid JSON, skip it
            continue
    
    return json_objects

def get_lines(prompt, batch):
    new_data = ''
    old_data = ''
    time.sleep(1.5)
    pyautogui.click()
    id = '"COMPLETED":' + f'"{random.randint(1, 10000)}"'
    pyperclip.copy(prompt + f" В конце json файла должна быть строчка json {id}")
    pyautogui.hotkey('ctrl', 'v')

    time.sleep(0.5)

    pyautogui.press('enter')
    time.sleep(8)

    pyautogui.move(0, -250)
    entry = time.time()
    timeout = False
    
    while True:
        pyautogui.click()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')

        try:
            new_data = pyperclip.paste()
        except:
            continue

        if new_data != old_data:
            old_data = new_data
        elif ('{' + id + '}') in new_data.replace(' ', ''):
            pyautogui.move(0, 250)
            return extract_json_from_text(new_data)[-2:-(batch + 2):-1]
        curr = time.time()
        if curr - entry > 180:
            timeout = True
            break

        time.sleep(0.3)
    
    if timeout:
        #input('Generation has been timed out. Ensure that the cursor is in the right position to insert the next batch-prompt into a text field of a chatbot and Press any key to continue, otherwise the progress mught be lost.')
        return 'STALLED'
    
            


