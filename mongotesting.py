import pymongo
from pymongo import MongoClient
import os

password = os.environ['mongo_pwd']

cluster = MongoClient("mongodb+srv://mongoadmin:{0}@cluster0.h0rrc.mongodb.net/?retryWrites=true&w=majority".format(password))
db = cluster['twittersentiment']
collection = db['emailmaster']

post = {"name":"NAME", "email": "EMAIL", "companies":["@Apple", "@Google"]}

#collection.insert_one(post)

results = collection.find({"companies":"@COMPANY"})
for result in results:
    print(result['name'])
print(collection.distinct("companies"))