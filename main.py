import twint
import pandas as pd
import nest_asyncio
import spacy
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os


nest_asyncio.apply()

nlp = spacy.load("en_core_web_sm", disable=['parser', 'tagger', 'ner'])
stops = stopwords.words("english")

analyser = SentimentIntensityAnalyzer()

def cleaner(t):
    t = t.lower()
    t = "".join(x for x in t if x.isalpha() or x.isspace())
    t = nlp(t)
    lemmatized = list()
    for word in t:
        lemma = word.lemma_.strip()
        if lemma:
            if lemma not in stops:
                lemmatized.append(lemma)
    return " ".join(lemmatized)

c=twint.Config()

queries = ["NuaWoman"]

for i in queries:
    filename = i+".csv"
    c.Search=[i]
    c.Limit=500
    c.Store_csv = True
    c.Output=filename
    c.Hide_output = True
    twint.run.Search(c)
    df = pd.read_csv(filename)
    tweets = list(df['tweet'])
    names = list(df['username'])
    tweets_copy = tweets
    tweets = [cleaner(t) for t in tweets]
    result = {'pos': 0, 'neg': 0, 'neu': 0}
    print(len(tweets))
    negatory_comments = []
    negatory_names = []
    for comment in tweets:
        score = analyser.polarity_scores(comment)
        if score['compound'] > 0.05:
            result['pos'] += 1
        elif score['compound'] < -0.05:
            result['neg'] += 1
            negatory_comments.append(tweets_copy[tweets.index(comment)])
        else:
            result['neu'] += 1
    for n in negatory_comments:
        negatory_names.append(names[negatory_comments.index(n)])    
    end_df = pd.DataFrame([negatory_names, negatory_comments])
    end_df.to_csv("End"+filename)
    print("{0}'s breakdown is".format(i))
    print(result)
    print(negatory_comments)
    os.remove(filename)