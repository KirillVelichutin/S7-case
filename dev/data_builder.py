import random
import json
from math import ceil

from tqdm import tqdm
from textnoisr import noise

from parse import count_tags, check_alignment
from screen_interractions import get_lines
from statics import DATAGEN, TAGS, PROMPT_KEYS, PROMPT_CONTEXT, ADDITIONAL


def replaceAndLabel(message, noise_level=0):
    noiser = noise.CharNoiseAugmenter(noise_level=noise_level, character_set='йцукенгшщзхфывапролджэячсмитьбю.,1234456789abcdefghijklmnopqrstuvwyz&*#$%',)
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
                rnd_data = str(noiser.add_noise(DATAGEN[tag]()))
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

def extract_context(path, window=6):

    with open(path) as f:
        lines = json.load(f)
    contexted = []
    for line in lines:
        for ent in line['entities']:
            tag = line['text'][ent[0]:ent[1]]
            splt = line['text'].split(tag)
            context = [obj.split() for obj in splt]
            left = " ".join(context[0][0:ceil(window/2)])
            right = " ".join(context[1][0:ceil(window/2)])
            context = f'{left} {tag} {right}'
            entities = [[len(left) + 1, len(left) + len(tag) + 1, ent[2]]]
            contexted.append({
                'text': context,
                'entities': entities
            })
    new_path = path.split('.')[0] + '_context' + str(random.randint(10000, 99999)) + '.json'
    with open(new_path, 'x') as f: 
        json.dump(contexted, f, ensure_ascii=False, indent=1, separators=(',', ': '))
    
    return new_path, contexted
            


    
def generate_data(size, export_file=None):

    tags = PROMPT_KEYS
    context = PROMPT_CONTEXT
    excluded_tags = []

    n_each = round(max(size / len(tags), 5))
    rel_batch = max(round(size / 100), 5)
    n_batch = rel_batch if rel_batch < 20 else 20
    
    total_tags_needed = len(tags) * n_each

    unprocessed = []
    data = []
    last_percentage = 0

    def save(export_file, data):
        random.shuffle(data)
        try:
            with open(export_file, 'x') as f:
                json.dump(data, f, ensure_ascii=False, indent=1, separators=(',', ': '))
        except:
            with open(export_file, 'w', encoding='utf-8') as f:
                f.truncate(0)
                json.dump(data, f, ensure_ascii=False, indent=1, separators=(',', ': '))
        try:
            with open(export_file + '_raw', 'x') as f:
                json.dump(unprocessed, f, ensure_ascii=False, indent=1, separators=(',', ': '))
        except:
            with open(export_file + '_raw', 'w', encoding='utf-8') as f:
                f.truncate(0)
                json.dump(unprocessed, f, ensure_ascii=False, indent=1, separators=(',', ': '))

    def tagcontext():
        tag_combo = '' 
        iter = random.randint(1, round(len(tags.keys()) / 2))
        for _ in range(iter):
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

        return tag_combo, context_combo
    
    def get_request():
        tag_combo, context_combo = tagcontext()
        request = f'сгенерируй {n_batch} строк в формате JSONL (каждая строчка формата "message": "_СООБЩЕНИЕ_") сообщений пользователей боту-помощнику авиакомпании, в которых они пишут ему свои персональные данные. Замени персональные данные в сообщениях специальными строками: {tag_combo}. В каждом сообщении встречаются все перечесленные теги.  Пользователи не здороваются. {context_combo} НЕ ПОВТОРЯЙ ФОРМУЛИРОВКИ. Самих данных в сообщении быть не должно - только перечисленные теги. Всегда добавляй контекст перед тегами. НЕ СМЕЙ ИГНОРИРОВАТЬ МОИ ИНСТРУКЦИИ.'
        return request

    print('\n'*2)
    with tqdm(total=100, colour="#2E271B", desc="generating data") as pbar:
        while len(excluded_tags) < len(set(tags)): # балансировка данных по тегам
            
            request = get_request()
            lines = [line for line in get_lines(request, n_batch)]

            # handling errors during generation
            while lines == ['S', 'T', 'A', 'L', 'L', 'E', 'D']:
                print('check')
                inp = input('the progress has stalled. type "y" to save the progress or any other key to continue: ')
                if inp == 'y':
                    save(export_file + '_unfinnished', data)
                    print('process was interrupted.')
                    return data
                request = get_request()
                lines = [line for line in get_lines(request, n_batch)]
            
            for obj in lines:
                try:
                    data.append(replaceAndLabel(obj['message']))
                    unprocessed.append(obj)
                    save(export_file, data)
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
            
            save(export_file, data)

    return data




