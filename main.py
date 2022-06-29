import twint
import pandas as pd
import nest_asyncio
import spacy
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
from datetime import datetime
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import yagmail

load_dotenv()
nest_asyncio.apply()

password = os.getenv('mongo_pwd')
email = os.getenv('email')
email_password = os.getenv('email_password')

cluster = MongoClient("mongodb+srv://mongoadmin:{0}@cluster0.h0rrc.mongodb.net/?retryWrites=true&w=majority".format(password))
db = cluster['twittersentiment']
collection = db['emailmaster']

nlp = spacy.load("en_core_web_sm", disable=['parser', 'tagger', 'ner'])
stops = stopwords.words("english")

analyser = SentimentIntensityAnalyzer()

yag = yagmail.SMTP(email, email_password)

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

def emailer(company, results, negative_tweets):
    query = {'company':company}
    mydoc = collection.find(query)
    addresses = []
    positive = results['pos']
    negative = results['neg']
    neutral = results['neu']
    for x in mydoc:
        addresses.append(x['email'])
    for e in addresses:
        yag.send(to=e, subject='Report About {0}'.format(company), contents='Hi! This is the report. Currently, out of the latest 500 tweets scraped and analysed, we found {0} positive tweets, {1} neutral tweets and {2} negative tweets. Attatched below is a CSV file of all negative tweets with username and tweet. Thanks!'.format(positive,neutral,negative), attachments=negative_tweets)
c=twint.Config()

queries = collection.distinct("company")
if len(queries)>0:
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
            end_df.to_csv("./tweetstorage/"+filename)
            print("{0}'s breakdown is".format(i))
            print(result)
            os.remove(filename)
            emailer(i,result,"./tweetstorage/"+filename )
        except:
            pass
else:
    print("No distinct companies.")
