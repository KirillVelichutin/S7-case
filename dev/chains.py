from random import choice as ch
from random import randint as ri
from random import shuffle
import json

from statics import HEAD, TOPIC, TIME, TAIL, DATE

####################################
#           TUNING CHAINS          #
####################################

with open('data/dostoevsky.txt', 'r', encoding='windows-1251') as f:
    book = f.read().replace('\n', ' ')

def get_str():
    rnd_start = ri(0, len(book) - 1000)
    return book[rnd_start:ri(rnd_start, rnd_start + ri(60, 200))]

rndchain = lambda: {'message': get_str()}

nocontext = lambda tag: {'message': tag}

####################################
#          DEFAULT CHAINS          #
####################################

defaultchain = lambda tag, context: {'message': f'{ch((ch(HEAD), '')) + ' '}{ch(((ch(TOPIC['question1']) + ' ' + ch(TOPIC['topic1']), ch(TOPIC['question2']) + ' ' + ch(TOPIC['topic2']))))}{ch(['', '.', ' -', ','])} {ch(context)} {tag} {ch('.,- ')} {ch((ch(TAIL), ''))}'}

doublechain = lambda tag1, tag2, context1, context2: {'message': ch((
    f'{ch((ch(HEAD), '')) + ' '} {ch('.,- ')} {ch(context1)} {tag1} {ch('.,- ')}{ch(((ch(TOPIC['question1']) + ' ' + ch(TOPIC['topic1']), ch(TOPIC['question2']) + ' ' + ch(TOPIC['topic2']))))}{ch(['', '.', ' -', ','])} {ch((ch(TAIL), ''))}',
    f'{ch((ch(HEAD), '')) + ' '} {ch('.,- ')} {ch(context2)} {tag2} {ch('.,- ')}{ch(((ch(TOPIC['question1']) + ' ' + ch(TOPIC['topic1']), ch(TOPIC['question2']) + ' ' + ch(TOPIC['topic2']))))}{ch(['', '.', ' -', ','])} {ch((ch(TAIL), ''))}',
    f'{ch((ch(HEAD), '')) + ' '}{ch(((ch(TOPIC['question1']) + ' ' + ch(TOPIC['topic1']), ch(TOPIC['question2']) + ' ' + ch(TOPIC['topic2']))))}{ch(['', '.', ' -', ','])} {ch(context1)} {tag1} {ch('.,- ')} {ch((ch(TAIL), ''))}',
    f'{ch((ch(HEAD), '')) + ' '}{ch(((ch(TOPIC['question1']) + ' ' + ch(TOPIC['topic1']), ch(TOPIC['question2']) + ' ' + ch(TOPIC['topic2']))))}{ch(['', '.', ' -', ','])} {ch(context2)} {tag2} {ch('.,- ')} {ch((ch(TAIL), ''))}',
    f'{ch((ch(HEAD), '')) + ' '} {ch('.,- ')} {ch(context2)} {tag2} в {tag1} {ch('.,- ')}{ch(((ch(TOPIC['question1']) + ' ' + ch(TOPIC['topic1']), ch(TOPIC['question2']) + ' ' + ch(TOPIC['topic2']))))}{ch(['', '.', ' -', ','])} {ch((ch(TAIL), ''))}',
    f'{ch((ch(HEAD), '')) + ' '} {ch('.,- ')} {ch(context2)} в {tag1} {tag2} {ch('.,- ')}{ch(((ch(TOPIC['question1']) + ' ' + ch(TOPIC['topic1']), ch(TOPIC['question2']) + ' ' + ch(TOPIC['topic2']))))}{ch(['', '.', ' -', ','])} {ch((ch(TAIL), ''))}',

))}

def extra_random(func):
    messagedict = func
    return {'message': ch((messagedict['message'] + ' ' + rndchain()['message'], rndchain()['message'] + ' ' + messagedict['message']))}

extrarandom = lambda func: extra_random(func)

####################################
#              BUILD               #
####################################

def build_chains(tag, context=TIME, path=f'./data/{ri(10000, 99999)}.json'):
    with open(path, 'w') as f:
        data = [defaultchain(tag, context) for i in range(220)] + [nocontext(tag) for i in range(20)] + [rndchain() for i in range(20)] + [extrarandom(defaultchain(tag, context)) for i in range(20)]
        shuffle(data)
        json.dump(data, f, ensure_ascii=False, indent=1, separators=(',', ': '))
    print(f'generated {len(data)} lines of text, saved to {path}')
    return data

def double_chains(tags=["TIME", "DATE"], context=[TIME, DATE], path=f'./data/{ri(10000, 99999)}.json'):
    with open(path, 'w') as f:
        extradata = [extrarandom(doublechain(tags[0], tags[1], context[0], context[1])) for i in range(150)]
        normaldata = [doublechain(tags[0], tags[1], context[0], context[1]) for i in range(250)]
        data = extradata + normaldata
        shuffle(data)
        json.dump(data[0:150], f, ensure_ascii=False, indent=1, separators=(',', ': '))
    print(f'generated {len(data)} lines of text, saved to {path}')
    return data

datechains = build_chains('DATE', path='./data/rawdate.json', context=DATE)
timechains = build_chains('DATE', path='./data/rawtime.json', context=TIME)
datetime = double_chains(path='data/doublechains.json')

with open('data/rawtimedate.json', 'w') as f:
    data = datechains + timechains + datetime
    shuffle(data)
    json.dump(data, f, ensure_ascii=False, indent=1, separators=(',', ': '))

# for i in range(10):
#     print(doublechain("TIME", "DATE", TIME, DATE))