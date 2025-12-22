import spacy

from get_datetime import parse_time, parse_date
from get_docs import process_request

rucore = spacy.load("ru_core_news_sm")
datetime = spacy.load('models/ru_date_time/model-best')
class S7ner():
    conversiontable = {
        'PER': 'person',
        'LOC': 'location'
    }

    standard = {
        'time': lambda time: parse_time(time),
        'date': lambda date: parse_date(date)
    }

    def __init__(self):
        self.rucore = spacy.load("ru_core_news_sm")
    

    def get_entities(self, text):
        tags = []

        rucore_doc = rucore(text)
        for ent in rucore_doc.ents:
            if ent.label_ in ("PER", "LOC"):
                tags.append((self.conversiontable[ent.label_], ent.text))

        timedate_doc = datetime(text)
        timedate_spans = timedate_doc.spans['sc']
        for span in timedate_spans:
            tags.append((span.label_, str(self.standard[span.label_](span.text)), span.text))

        docs = process_request(text)
            
        return tags + docs


if __name__ == "__main__":
    ner = S7ner()
    message = "здравствуйте! время вылета 17:30, дата первое марта. меня зоыут владимир путин и я лечу в индию. мой паспорт 4018294647 мой номер телефона 89112800812 мой имейл nikitasemin@gmail.com ".lower()
    print(message)
    doc = ner.get_entities(message)
    for tag in doc:
        print(tag)


