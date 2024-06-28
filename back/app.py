import json
import requests
import config
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import any_
from flask_migrate import Migrate

from jp_parse import jpWordExtract

# Initialization & config

app = Flask(__name__)
CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = './'
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL

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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    episode_no = db.Column(db.Integer, index=True)
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
    episode_id = db.Column(db.Integer, db.ForeignKey(Episode.id))
    name = db.Column(db.String)
    link = db.Column(db.String)

    def __init__(self, episode_id, name=None, link=None):
        self.episode_id= episode_id
        self.name = name
        self.link = link

# Routes

# Test route
@app.route('/')
@cross_origin()
def hello():
    return "Hello, world!"


@app.route('/check_episode', endpoint='/check_episode', methods=['GET'])
@cross_origin()
def check_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))

    # Insert show into DB if it doesn't exist
    if Show.query.filter(Show.id == showId).count() == 0:
        showToInsert = Show(showId)
        db.session.add(showToInsert)
        db.session.commit()
    
    # Insert episode into DB if it doesn't exist
    if Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).count() == 0:
        episodeToInsert = Episode(episodeNo, showId)
        db.session.add(episodeToInsert)
        db.session.commit()
        return Response(response=json.dumps({ "episode_exists": False }), mimetype='application/json')
    else:
        return Response(response=json.dumps({ "episode_exists": True}), mimetype='application/json')


@app.route('/get_subtitles', endpoint='/get_subtitles', methods=['GET'])
@cross_origin()
def get_subtitles():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    episodeId = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first().id

    jimakuKey = config.JIMAKU_KEY

    # Retrieve Jimaku ID for series
    searchUrl = "https://jimaku.cc/api/entries/search"
    searchHeaders = { "Authorization": jimakuKey }
    searchParams = { "anilist_id": showId }
    searchResponse = requests.get(searchUrl, headers=searchHeaders, params=searchParams).json()

    # Retrieve all subtitle files for given episode
    jimakuId = searchResponse[0]['id']
    filesUrl = f"https://jimaku.cc/api/entries/{jimakuId}/files"
    filesHeader = { "Authorization": jimakuKey }
    filesParams = { "episode": episodeNo }
    filesResponse = requests.get(filesUrl, headers=filesHeader, params=filesParams).json()

    link = ""

    # Insert subtitles and retrieve URL to parse
    for subtitle in filesResponse:
        if subtitle['url'].endswith(".ass") or subtitle['url'].endswith(".srt"):
            link = subtitle['url']
            subtitleName = subtitle['name']
            subtitleLink = subtitle['url']
            subtitleToInsert = Subtitle(episodeId, subtitleName, subtitleLink)
            db.session.add(subtitleToInsert)
    db.session.commit()

    return Response(response=json.dumps({ "subtitle_url": link }))


@app.route('/analyze_episode', endpoint='/analyze_episode', methods=['POST'])
@cross_origin()
def analyze_episode():
    text = request.form['data']
    resultDict = jpWordExtract(text)

    allWords = []
    for word in resultDict:
        allWords.append(word)
    
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    
    episode = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()
    episode.words = allWords
    db.session.commit()
    
    return Response(response=json.dumps(allWords), mimetype='application/json')


@app.route('/get_episode', endpoint='/get_episode', methods=['GET'])
@cross_origin()
def get_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    offset = int(request.args.get('offset'))

    words = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()
    if words is None:
        return Response(response=json.dumps({ "error": "The requested episode was not found." }), mimetype='application/json')
    
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