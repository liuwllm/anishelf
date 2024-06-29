import os
import json
import requests
import config
import pysubs2
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import any_, or_, and_
from sqlalchemy import desc
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
    episodes = db.relationship('Episode', backref='show')

    def __init__(self, id):
        self.id = id


class Episode(db.Model):
    __tablename__ = 'episodes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    episode_no = db.Column(db.Integer, index=True)
    show_id = db.Column(db.Integer, db.ForeignKey(Show.id), index=True)
    subtitles = db.relationship('Subtitle', backref='episode')
    words = db.relationship('EpisodeWord', backref='episode')
    
    def __init__(self, episode_no=None, show_id=None):
        self.episode_no = episode_no
        self.show_id = show_id


class Subtitle(db.Model):
    __tablename__ = 'subtitles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    episode_id = db.Column(db.Integer, db.ForeignKey(Episode.id))
    name = db.Column(db.String)
    link = db.Column(db.String)
    last_modified = db.Column(db.String)
    size = db.Column(db.Integer)

    def __init__(self, episode_id, name=None, link=None, last_modified=None, size=None):
        self.episode_id= episode_id
        self.name = name
        self.link = link
        self.last_modified = last_modified
        self.size = size

class EpisodeWord(db.Model):
    __tablename__ = 'episodewords'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    episode_id = db.Column(db.Integer, db.ForeignKey(Episode.id))
    word = db.Column(db.String)
    frequency = db.Column(db.Integer)

    def __init__(self, episode_id=None, word=None, frequency=None):
        self.episode_id = episode_id
        self.word = word
        self.frequency = frequency

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
            subtitleName = subtitle['name']
            subtitleLink = subtitle['url']
            subtitleModified = subtitle['last_modified']
            subtitleSize = subtitle['size']
            subtitleToInsert = Subtitle(episodeId, subtitleName, subtitleLink, subtitleModified, subtitleSize)
            db.session.add(subtitleToInsert)
        if subtitle['url'].endswith(".ass") and link == "":
            link = subtitle['url']
        elif subtitle['url'].endswith(".srt"):
            link = subtitle['url']
    db.session.commit()

    return Response(response=json.dumps({ "subtitle_url": link }))


@app.route('/analyze_episode', endpoint='/analyze_episode', methods=['POST'])
@cross_origin()
def analyze_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    episodeId = Episode.query.with_entities(Episode.id).filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()[0]

    subUrl = request.form['url']
    subType = request.form['type']
    subResponse = requests.get(subUrl).content

    subPath = os.path.join(app.config['UPLOAD_FOLDER'], f'subtitle{subType}')

    with open(subPath, 'wb') as file:
        file.write(subResponse)
    
    subs = pysubs2.load(subPath)
    print(subs)

    combinedText = ""
    for line in subs:
        combinedText += line.text

    resultDict = jpWordExtract(combinedText)
    
    for word in resultDict:
        episodeWord = EpisodeWord(episodeId, word, resultDict[word])
        db.session.add(episodeWord)
    db.session.commit()
    
    return Response(response=json.dumps(resultDict), mimetype='application/json')


@app.route('/get_episode', endpoint='/get_episode', methods=['GET'])
@cross_origin()
def get_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    offset = int(request.args.get('offset'))

    episode = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()
    if episode is None:
        return Response(response=json.dumps({ "error": "The requested episode was not found." }), mimetype='application/json')
    
    vocabToSearch = EpisodeWord.query.filter(EpisodeWord.episode_id == episode.id).order_by(desc(EpisodeWord.frequency)).limit(20).offset(offset).all()

    prev = False
    next = False
    if offset != 0:
        prev = True
    if EpisodeWord.query.filter(EpisodeWord.episode_id == episode.id).count() > (offset + 20):
        next = True

    finalVocab = []
    for vocab in vocabToSearch:
        kebFind = Word.query.filter(vocab.word == any_(Word.keb)).all()
        if kebFind:
            for word in kebFind:
                finalVocab.append({
                    'id': word.id,
                    'keb': word.keb,
                    'reb': word.reb,
                    'sense': word.sense
                })
        else:
            rebFind = Word.query.filter(
                and_(
                    vocab.word == any_(Word.reb), 
                    Word.keb == '{}'
                )
            ).all()
            for word in rebFind:
                finalVocab.append({
                    'id': word.id,
                    'keb': word.keb,
                    'reb': word.reb,
                    'sense': word.sense
                })

    return Response(response=json.dumps({ "vocab": finalVocab, "prev": prev, "next": next}), mimetype='application/json')