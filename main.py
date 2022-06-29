import twint
import pandas as pd
import nest_asyncio
import spacy
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
from datetime import datetime


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

queries = ["@nuawoman"]

for i in queries:
    filename = i+".csv"
    c.Search=[i]
    c.Limit=500
    c.Store_csv = True
    c.Output=filename
    c.Hide_output = True
    twint.run.Search(c)
    try:
        df = pd.read_csv(filename)
        tweets = list(df['tweet'])
        names = list(df['username'])
        tweets_copy = tweets
        tweets = [cleaner(t) for t in tweets]
        print(len(tweets))
        result = {'pos': 0, 'neg': 0, 'neu': 0}
        negatory_comments = []
        negatory_names = []
        for comment in tweets:
            score = analyser.polarity_scores(comment)
            if score['compound'] > 0.05:
                result['pos'] += 1
            elif score['compound'] < -0.05:
                result['neg'] += 1
                negatory_comments.append(tweets_copy[tweets.index(comment)])
                negatory_names.append(names[tweets.index(comment)])
            else:
                result['neu'] += 1
        end_df = pd.DataFrame({"Name": negatory_names, "Tweet": negatory_comments})
        end_df.to_csv("({0})".format(datetime.now())+filename)
        print("{0}'s breakdown is".format(i))
        print(result)
        print(negatory_comments)
        os.remove(filename)
    except:
        pass
