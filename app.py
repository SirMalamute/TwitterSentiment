from flask import Flask, render_template, request, redirect, url_for
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

password = os.getenv('mongo_pwd')

cluster = MongoClient("mongodb+srv://mongoadmin:{0}@cluster0.h0rrc.mongodb.net/?retryWrites=true&w=majority".format(password))
db = cluster['twittersentiment']
collection = db['emailmaster']

app = Flask(__name__)

def get_unique():
    try:
        return collection.distinct("company")
    except:
        return ""

@app.route('/')
def index():
    return render_template("TwitterSentiment.html", companies=get_unique())
@app.route('/handle_data', methods=['GET', 'POST'])
def handle_data():
    company = request.form['name']
    email = request.form['email']
    post = {"company":company, "email":email}
    collection.insert_one(post)
    return redirect(url_for("index"))
