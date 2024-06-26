import os
import json
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import any_
from flask_migrate import Migrate
from dotenv import load_dotenv
from jp_parse import jpWordExtract

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
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, index=True)
    keb = db.Column(db.ARRAY(db.String), index=True)
    reb = db.Column(db.ARRAY(db.String), index=True)
    sense = db.Column(db.ARRAY(db.String))

    def __init__(self, id, keb=None, reb=None, sense=None):
        self.id = id
        self.keb = keb
        self.reb = reb
        self.sense = sense


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, index=True)
    words = db.Column(db.ARRAY(db.String))
    episodes = db.relationship('Episode', backref='show')

    def __init__(self, id, words=None):
        self.id = id
        self.words = words


class Episode(db.Model):
    __tablename__ = 'episodes'
    episode_no = db.Column(db.Integer, primary_key=True, index=True)
    show_id = db.Column(db.Integer, db.ForeignKey(Show.id), index=True)
    words = db.Column(db.ARRAY(db.String))
    subtitles = db.relationship('Subtitle', backref='episode')
    
    def __init__(self, episode_no, show_id, words=None):
        self.episode_no = episode_no
        self.show_id = show_id
        self.words = words


class Subtitle(db.Model):
    __tablename__ = 'subtitles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    episode_no = db.Column(db.Integer, db.ForeignKey(Episode.episode_no))
    name = db.Column(db.String)
    link = db.Column(db.String)

    def __init__(self, episode_no, name=None, link=None):
        self.episode_no = episode_no
        self.name = name
        self.link = link

# Routes

# Test route
@app.route('/')
def hello():
    return "Hello, world!"


@app.route('/check_episode', endpoint='/check_episode', methods=['GET'])
@cross_origin
def check_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    if Show.query.filter(Show.id == showId).count() == 0:
        showToInsert = Show(showId)
        db.session.add(showToInsert)
        db.session.commit()
    if Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).count() == 0:
        return Response(response=json.dumps({ "episode_exists": False }, mimetype='application/json'))
    else:
        return Response(response=json.dumps({ "episode_exists": True}, mimetype='application/json'))


@app.route('/analyze_episode', endpoint='/analyze_episode', methods=['POST'])
@cross_origin
def analyze_episode():
    text = request.form['data']
    resultDict = jpWordExtract(text)

    allWords = []
    for word in resultDict:
        allWords.append(word)
    
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))

    episodeToInsert = Episode(showId, episodeNo, allWords)
    db.session.add(episodeToInsert)
    db.session.commit()

    for subtitle in request.form['sub']:
        subtitleName = subtitle['name']
        subtitleLink = subtitle['link']
        subtitle = Subtitle(episodeNo, subtitleName, subtitleLink)
        db.session.add(subtitle)
    db.session.commit()
    
    return Response(response=json.dumps(allWords), mimetype='application/json')


@app.route('/get_episode', endpoint='/get_episode', methods=['GET'])
@cross_origin
def get_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    offset = int(request.args.get('offset'))

    words = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()
    if words is None:
        return Response(response=json.dumps({ "error": "The requested episode was not found." }))
    
    numberOfWords = len(words.words)

    allWords = []

    for i in range(0 + offset, 20 + offset):
        if i > numberOfWords:
            break
        results = Word.query.filter(words.words[i] == any_(Word.keb)).all()
        if not results:
            results = Word.query.filter(words.words[i] == any_(Word.reb), Word.keb =='{}').all()
        for result in results:
            allWords.append(result)

    return Response(response=json.dumps({ "words": allWords }), mimetype='application/json')