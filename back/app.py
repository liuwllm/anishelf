import os
import json
import requests
import config
import pysubs2
from flask import Flask, Response, request
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import any_, or_, and_
from sqlalchemy import desc, func
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
    episodewords = db.relationship('EpisodeWord', backref='show')

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
    show_id = db.Column(db.Integer, db.ForeignKey(Show.id))
    episode_id = db.Column(db.Integer, db.ForeignKey(Episode.id))
    word = db.Column(db.String)
    frequency = db.Column(db.Integer)

    def __init__(self, show_id=None, episode_id=None, word=None, frequency=None):
        self.show_id = show_id
        self.episode_id = episode_id
        self.word = word
        self.frequency = frequency

# Utility functions
def searchWords(episode_id):
    finalVocab = db.session.query(EpisodeWord).join(
        Word, 
        or_(
            (EpisodeWord.word == any_(Word.keb)),
            (and_(
                (EpisodeWord.word == any_(Word.reb)),
                (Word.keb == '{}')
            ))
        )
    ).filter(EpisodeWord.episode_id == episode_id).order_by(desc(EpisodeWord.frequency)).all()
    return finalVocab

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

    # Insert subtitles and retrieve URL to parse
    for subtitle in filesResponse:
        if subtitle['url'].endswith(".ass") or subtitle['url'].endswith(".srt"):
            subtitleName = subtitle['name']
            subtitleLink = subtitle['url']
            subtitleModified = subtitle['last_modified']
            subtitleSize = subtitle['size']
            subtitleToInsert = Subtitle(episodeId, subtitleName, subtitleLink, subtitleModified, subtitleSize)
            db.session.add(subtitleToInsert)

    link = Subtitle.query.filter(Subtitle.episode_id == episodeId).first().link

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

    combinedText = ""
    for line in subs:
        combinedText += line.text
        print(line)

    resultDict = jpWordExtract(combinedText)
    
    for word in resultDict:
        episodeWord = EpisodeWord(showId, episodeId, word, resultDict[word])
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

    finalVocab = searchWords(vocabToSearch)

    return Response(response=json.dumps({ "vocab": finalVocab, "prev": prev, "next": next}), mimetype='application/json')

@app.route('/export_episode', endpoint='/export_episode', methods=['GET'])
@cross_origin()
def export_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))

    episode = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()
    if episode is None:
        return Response(response=json.dumps({ "error": "The requested episode was not found." }), mimetype='application/json')
    
    finalVocab = searchWords(episode.id)

    return Response(response=json.dumps(finalVocab), mimetype='application/json')
'''
@app.route('/get_show', endpoint='/get_show', methods=['GET'])
@cross_origin()
def get_show():
    showId = int(request.args.get('anilist_id'))
    offset = int(request.args.get('offset'))
    
    vocabToSearch = db.session.query(
        EpisodeWord.episode_id,
        EpisodeWord.word,
        func.sum(EpisodeWord.frequency).label('total_frequency')
    ).filter(
        EpisodeWord.show_id == showId
    ).group_by(
        EpisodeWord.episode_id,
        EpisodeWord.word
    ).order_by(
        desc(EpisodeWord.frequency)
    ).limit(20).offset(offset).all()

    prev = False
    next = False
    if offset != 0:
        prev = True
    if db.session.query(
        EpisodeWord.episode_id,
        EpisodeWord.word,
        func.sum(EpisodeWord.frequency).label('total_frequency')
    ).filter(
        EpisodeWord.show_id == showId
    ).group_by(
        EpisodeWord.episode_id,
        EpisodeWord.word
    ).count() > (offset + 20):
        next = True

    finalVocab = searchWords(vocabToSearch)

    return Response(response=json.dumps({ "vocab": finalVocab, "prev": prev, "next": next}), mimetype='application/json')

@app.route('/export_show', endpoint='/export_show', methods=['GET'])
@cross_origin()
def export_show():
    showId = int(request.args.get('anilist_id'))
    
    vocabToSearch = db.session.query(
        EpisodeWord.episode_id,
        EpisodeWord.word,
        func.sum(EpisodeWord.frequency).label('total_frequency')
    ).filter(
        EpisodeWord.show_id == showId
    ).group_by(
        EpisodeWord.episode_id,
        EpisodeWord.word
    ).order_by(
        desc(EpisodeWord.frequency)
    ).all()

    finalVocab = searchWords(vocabToSearch)

    return Response(response=json.dumps(finalVocab), mimetype='application/json')
'''

@app.route('/download_subtitles', endpoint='/download_subtitles', methods=['GET'])
@cross_origin()
def download_subtitles():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))

    episode = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()
    subtitles = Subtitle.query.filter(Subtitle.episode_id == episode.id).all()

    res = []
    for subtitle in subtitles:
        res.append({
            "id": subtitle.id,
            "name": subtitle.name,
            "link": subtitle.link,
            "size": subtitle.size,
            "last_modified": subtitle.last_modified
        })
    
    return Response(response=json.dumps(res), mimetype='application/json')