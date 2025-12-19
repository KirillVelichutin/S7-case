import spacy
from spacy.training import Example

import random
import json

from data_builder import TAGS
from parse import examples

def train_model(training_data, n_iters=20, model_name=None):

    nlp = spacy.load(model_name)
    
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    for tag in ['DATE']:
        ner.add_label(tag)

    print(f'training for the recognition of the following labels: {list(ner.labels)}')

    with nlp.disable_pipes([pipe for pipe in nlp.pipe_names if pipe != "ner"]):
        nlp.begin_training()
        
        for itn in range(n_iters):

            losses = {}

            for batch in spacy.util.minibatch(training_data, 20):
                # for text, example in batch:
                #     print(spacy.training.offsets_to_biluo_tags(nlp.make_doc(text), example['entities']))
                # return 0
                examples = [Example.from_dict(nlp.make_doc(text), example) for text, example in batch]
                nlp.update(examples, drop=0.5, losses=losses)
            print(losses)

            if int(losses.get('ner', 0)) < 1:    
                model_path = f'models/model_{random.randint(1000000, 2000000)}'
                nlp.to_disk(model_path)
                print(f'\nmodel saved to {model_path}')
                return model_path



#     doc = nlp('Приветствую! Для получения бонусных миль: Галина Вячеславовна Гурьева, 91 30 331597, ostromir2018@example.net')
#     if doc.ents:
#         for ent in doc.ents:
#             print(f"   ✅ {ent.label_}: '{ent.text}'")
#     else:
#         print("   ❌ No entities found")

data = examples('data/only_dates.json')

path = train_model(data, 300, 'ru_core_news_sm')

#models/model_1425355
#load_model(path)