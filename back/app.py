import os
import json
from flask import Flask, Response
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Initialization & config

app = Flask(__name__)
CORS(app)

load_dotenv()
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = './'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Models

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    keb = db.Column(db.ARRAY(db.String))
    reb = db.Column(db.ARRAY(db.String))
    sense = db.Column(db.ARRAY(db.String))

    def __init__(self, id, keb=None, reb=None, sense=None):
        self.id = id
        self.keb = keb
        self.reb = reb
        self.sense = sense

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    words = db.Column(db.ARRAY(db.Integer))
    episodes = db.relationship('Episode', backref='show')

    def __init__(self, id, words=None):
        self.id = id
        self.words = words

class Episode(db.Model):
    __tablename__ = 'episodes'
    episode_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey(Show.id))
    words = db.Column(db.ARRAY(db.Integer))
    subtitles = db.relationship('Subtitle', backref='episode')
    
    def __init__(self, show_id, words=None):
        self.show_id = show_id
        self.words = words

class Subtitle(db.Model):
    __tablename__ = 'subtitles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    episode_id = db.Column(db.Integer, db.ForeignKey(Episode.episode_id))
    name = db.Column(db.String)
    link = db.Column(db.String)

    def __init__(self, episode_id, name=None, link=None):
        self.episode_id = episode_id
        self.name = name
        self.link = link

# Routes

# Test route
@app.route('/')
def hello():
    return "Hello, world!"

@app.route('/analyze', methods=['POST'])
def analyze():
    return "PLACEHOLDER"
