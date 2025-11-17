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
        
        new_data = pyperclip.paste()
       # print(extract_json_from_text(new_data)[:batch + 2:1])
        if new_data != old_data:
            old_data = new_data
        elif ('{' + id + '}') in new_data.replace(' ', ''):
            pyautogui.move(0, 250)
            return extract_json_from_text(new_data)[-2:-(batch + 2):-1]
        curr = time.time()
        if curr - entry > 80:
            timeout = True
            break

        time.sleep(0.3)
    
    if timeout:
        #input('Generation has been timed out. Ensure that the cursor is in the right position to insert the next batch-prompt into a text field of a chatbot and Press any key to continue, otherwise the progress mught be lost.')
        input('stalled.')
        return {'message': 'дата DATE телефон PHONE почта EMAIL время TIME спасибо'}
    
            

if __name__ == '__main__':
    prompt = "сгенерируй 5 строк в формате JSONL (каждаф строчка формата {'message': '_СООБЩЕНИЕ_'}) сообщений пользователей боту-помощнику авиакомпании, в которых они пишут ему свои персональные данные. Замени персональные данные в сообщениях специальными строками: номер паспорта - PASSPORT, дата рождения - DOB, номер билета - TICKET_NUMBER. В каждом сообщении встречаются все перечесленные теги. Пользователи иногда пишут неграмотно, встречаются сообщения разной длины. Теги не встречаются без контекста - в сообщении всегда есть другие слова. Иногда, но редко, пользователи пишут грубо. Пользователи часто не здороваются, иногда печатают в спешке. Старайся не повторять формулировки."
    data = get_lines(prompt, 5)
    for line in data:
        print(line)

