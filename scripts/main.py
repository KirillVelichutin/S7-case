import spacy

from get_datetime import parse_time, parse_date, ngrams
from get_docs import process_request
from get_airports import get_airports, is_airport

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

        #date and time
        sliced_message = ngrams(text)
        for ngram in sliced_message:
            timedate_doc = datetime(ngram)
            timedate_spans = timedate_doc.spans['sc']
            for span in timedate_spans:
                tags.append((span.label_, str(self.standard[span.label_](span.text)), span.text))
        tags = list(set(tags))

        #reolving conflicts
        for item in tags:
            try:
                int(''.join(''.join(item[1].split('-')).split(':'))) # checking for failed parses
            except:
                tags.pop(tags.index(item))

        #remove repeating items       
        seen = set()
        tags = [t for t in tags if not (t[0] in {'date', 'time'} and t[1] in seen or seen.add(t[1]))]
        #check if the contents partially repeat
        def is_close(t1, t2, message):
            threshold = len(t1)
            p1, p2 = message.find(t1), message.find(t2)
            if p1 != -1 and p2 != -1 and abs(p1 - p2) <= threshold:
                return message[p1:p2+len(t2)]

        for item1 in tags:
            for item2 in tags:
                if item1 != item2:
                    connected = is_close(item1[2], item2[2], text)
                    tag1 = item1[0]
                    tag2 = item2[0]
                    if connected and tag1 == tag2:
                        tags.pop(tags.index(item1))
                        tags.pop(tags.index(item2))
                        tags.append((tag1, str(self.standard[tag1](connected)), connected))


        #people and locations
        rucore_doc = rucore(text)
        locs = []
        for ent in rucore_doc.ents:
            if ent.label_ == "PER":
                tags.append((self.conversiontable[ent.label_], ent.text))
            if ent.label_ == "LOC":
                locs.append(ent.text)
        
        #documents and standardized data
        docs = process_request(text)
        
        #finding airport names, resolving airport/location conflict
        airports = get_airports(text)

        for airport in airports:
            for loc in locs:
                if airport == is_airport(loc):
                    locs.pop(locs.index(loc))
        for loc in locs:
            tags.append(('location', loc))
        for airport in airports:
            tags.append(('airport', airport))
                
        return tags + docs


if __name__ == "__main__":
    ner = S7ner()
    message = "здравствуйте! время вылета 17:30, дата первое марта. меня зоыут владимир путин и я лечу в индию из домодедова в грозный. мой паспорт 4018294647 мой номер телефона 89112800812 мой имейл nikitasemin@gmail.com ".lower()
    while True:
        message = input('type: ')
        doc = ner.get_entities(message)
        for tag in doc:
            print(tag)


