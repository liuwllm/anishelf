import os
import json
import requests
import pysubs2
import regex as re
from . import anishelf_bp
from ..config import settings
from ..database import db
from flask import Response, request
from flask_cors import cross_origin
from sqlalchemy.sql import any_, or_, and_
from sqlalchemy.orm import aliased
from sqlalchemy import desc, func, text
from ..models.episode import Episode
from ..models.episodeword import EpisodeWord
from ..models.show import Show
from ..models.subtitle import Subtitle
from ..models.word import Word
from ..utils.jp_parse import jpWordExtract


def checkKanji(word):
    return re.match(r'\p{Han}', word)


def searchWords(episode_id, paginate, offset=None):
    epId = episode_id

    finalVocab = EpisodeWord.query.with_entities(
            Word.id,
            Word.keb,
            Word.reb,
            Word.sense
        ).select_from(EpisodeWord) \
        .join(
            Word, 
            or_(
                EpisodeWord.word == Word.keb,
                EpisodeWord.word == Word.reb
            )
        ).filter(EpisodeWord.episode_id == epId) \
        .order_by(desc(EpisodeWord.frequency)) \
        .all()
    
    if paginate:
        finalVocab = finalVocab[offset: offset + 20]

    return [{
                "id": word.id, 
                "keb": word.keb, 
                "reb": word.reb, 
                "sense": word.sense 
            } for word in finalVocab]

# Test route
@anishelf_bp.route('/')
@cross_origin()
def hello():
    return "Hello, world!"


@anishelf_bp.route('/check_episode', endpoint='/check_episode', methods=['GET'])
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
    
    # Check if episode entry has no vocabulary
    elif EpisodeWord.query.filter(EpisodeWord.episode_id == episodeNo, EpisodeWord.show_id == showId).count() == 0:
        return Response(response=json.dumps({ "episode_exists": False }), mimetype='application/json')
    
    else:
        return Response(response=json.dumps({ "episode_exists": True}), mimetype='application/json')



@anishelf_bp.route('/get_subtitles', endpoint='/get_subtitles', methods=['GET'])
@cross_origin()
def get_subtitles():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    episodeId = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first().id

    jimakuKey = settings.JIMAKU_KEY

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


@anishelf_bp.route('/analyze_episode', endpoint='/analyze_episode', methods=['POST'])
@cross_origin()
def analyze_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    episodeId = Episode.query.with_entities(Episode.id).filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()[0]

    subUrl = request.form['url']
    subType = request.form['type']
    subResponse = requests.get(subUrl).content

    subPath = os.path.join(settings.UPLOAD_FOLDER, f'subtitle{subType}')

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


@anishelf_bp.route('/get_episode', endpoint='/get_episode', methods=['GET'])
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
        if checkKanji(vocab.word):
            kebFind = Word.query.filter(vocab.word == Word.keb).all()
            if kebFind:
                for word in kebFind:
                    finalVocab.append({
                        'id': word.id,
                        'keb': word.keb,
                        'reb': word.reb,
                        'sense': word.sense
                    })
        else:
            rebFind = Word.query.filter(and_(vocab.word == Word.reb, Word.keb == None)).all()
            if rebFind:
                for word in rebFind:
                    finalVocab.append({
                        'id': word.id,
                        'keb': word.keb,
                        'reb': word.reb,
                        'sense': word.sense
                    })

    return Response(response=json.dumps({ "vocab": finalVocab, "prev": prev, "next": next}), mimetype='application/json')


@anishelf_bp.route('/export_episode', endpoint='/export_episode', methods=['GET'])
@cross_origin()
def export_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))

    episode = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()
    if episode is None:
        return Response(response=json.dumps({ "error": "The requested episode was not found." }), mimetype='application/json')
    
    finalVocab = searchWords(episode.id, False)

    return Response(response=json.dumps(finalVocab), mimetype='application/json')


@anishelf_bp.route('/download_subtitles', endpoint='/download_subtitles', methods=['GET'])
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