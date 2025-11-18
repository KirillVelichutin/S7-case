import random
import json

from tqdm import tqdm

from parse import count_tags
from screen_interractions import get_lines
from statics import DATAGEN, TAGS, PROMPT_KEYS, PROMPT_CONTEXT

def replaceAndLabel(message):

    obj = {
        'text': message,
        'entities': []
    }

    tmp_entities = {}

    # inserting generated data
    for tag in TAGS:

        if tag in message:
            split_message = [part for part in obj['text'].split(tag)]
            augmented_message = ''
            
            for i in range(len(split_message) - 1):
                rnd_data = str(DATAGEN[tag]())
                tmp_entities[rnd_data] = tag
                augmented_message += f'{split_message[i]}{rnd_data}'
                
                if i == len(split_message) - 2:
                    augmented_message += split_message[i + 1]
            if len(augmented_message) < 2:
                augmented_message = f'ERROR: {obj['text']}'
            obj['text'] = augmented_message
    
    # marking out the message
    for key in tmp_entities:
        obj['entities'].append((obj['text'].find(key), obj['text'].find(key) + len(key), tmp_entities[key]))
    
    return obj

    
def generate_data(size, export_file=None):

    tags = PROMPT_KEYS
    context = PROMPT_CONTEXT
    excluded_tags = []

    n_each = round(max(size / len(tags), 5))
    rel_batch = max(round(size / 100), 5)
    n_batch = rel_batch if rel_batch < 20 else 20
    
    total_tags_needed = len(tags) * n_each

    data = []
    last_percentage = 0

    print('\n'*2)
    with tqdm(total=100, colour="#2E271B", desc="generating data") as pbar:
        while len(excluded_tags) < len(set(tags)): # балансировка данных по тегам

            tag_combo = '' 
            for _ in range(random.randint(1, round(len(tags.keys()) / 2))):
                while True:
                    new_tag = random.choice([key for key in list(tags.keys()) if key not in excluded_tags])
                    if new_tag not in tag_combo and new_tag not in excluded_tags:
                        tag_combo += tags[new_tag] + ', '
                        break
                    else:
                        break
        
            context_list = []
            rnd_iter = random.randint(1, len(context) - 1)
            for _ in range(rnd_iter):
                while len(context_list) < rnd_iter:
                    new_str = random.choice(context)()
                    if new_str not in context_list:
                        context_list.append(new_str)
            context_combo = ' '.join(context_list)


            request = f'сгенерируй {n_batch} строк в формате JSONL (каждая строчка формата "message": "_СООБЩЕНИЕ_") сообщений пользователей боту-помощнику авиакомпании, в которых они пишут ему свои персональные данные. Замени персональные данные в сообщениях специальными строками: {tag_combo}. В каждом сообщении встречаются все перечесленные теги. Теги не встречаются без контекста - в сообщении всегда есть другие слова. Пользователи не здороваются. {context_combo} Не повторяй формулировки'
            
            lines = [line for line in get_lines(request, n_batch)]

            for obj in lines:
                try:
                    data.append(replaceAndLabel(obj['message']))
                except:
                    pass
            
            count = count_tags(dict=data)
            total = count['total_tags']

            current_percentage = min(round(total / (total_tags_needed / 100)), 100)
            pbar.update(current_percentage - last_percentage)
            last_percentage = current_percentage
            pbar.refresh()
            

            for tag in tags.keys():
                if tag in count.keys() and int(count[tag]) >= n_each:
                    if tag not in excluded_tags:
                        excluded_tags.append(tag)


    print(data[0:10])
    
    if export_file:
        try:
            with open(export_file, 'x') as f:
                json.dump(data, f, ensure_ascii=False, indent=1, separators=(',', ': '))
        except:

            with open(export_file, 'w', encoding='utf-8') as f:
                f.truncate(0)
                json.dump(data, f, ensure_ascii=False, indent=1, separators=(',', ': '))
    
    return data







