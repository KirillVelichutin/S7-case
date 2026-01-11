from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os

df = pd.read_csv(os.path.join('../data', 'airports_rus.csv'))
airports_raw = df[['Название аэропорта']].dropna().reset_index(drop=True)['Название аэропорта'].tolist()
airports = [phrase.split()[0].lower() for phrase in airports_raw]

def most_similar(target, words):
    vectorizer = CountVectorizer(analyzer='char', ngram_range=(1,2))
    vectors = vectorizer.fit_transform([target] + words)
    similarities = cosine_similarity(vectors[0:1], vectors[1:])[0]
    if similarities.max() < 0.8:
        return None
    return words[similarities.argmax()]

def is_airport(token):
    return most_similar(token, airports)  

def get_airports(sentence):
    tokens = sentence.split()
    airports = []
    for token in tokens:
        result = is_airport(token)
        if result:
            airports.append(result)
    return airports