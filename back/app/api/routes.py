import os, json, requests, pysubs2
from . import anishelf_bp
from ..config import settings
from ..database import db
from flask import Response, request
from flask_cors import cross_origin
from sqlalchemy.sql import or_, and_
from sqlalchemy import desc
from ..models.episode import Episode
from ..models.episodeword import EpisodeWord
from ..models.show import Show
from ..models.subtitle import Subtitle
from ..models.word import Word
from ..utils.jp_parse import jpWordExtract, checkKanji


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
    episodeId = Episode.query.with_entities(Episode.id).filter_by(episode_no=episodeNo, show_id=showId)

    if EpisodeWord.query.filter(EpisodeWord.episode_id == episodeId, EpisodeWord.show_id == showId).count() == 0:
        return Response(response=json.dumps({ "episode_exists": False }), mimetype='application/json')
    else:
        return Response(response=json.dumps({ "episode_exists": True}), mimetype='application/json')



# Endpoint to insert subtitles data if not existing and retrieve first subtitle file for further processing
@anishelf_bp.route('/get_subtitles', endpoint='/get_subtitles', methods=['GET'])
@cross_origin()
def get_subtitles():
    # Get show ID and episode number and use to find episode ID
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


# Endpoint to retrieve frequency of vocabulary and add to database
@anishelf_bp.route('/analyze_episode', endpoint='/analyze_episode', methods=['POST'])
@cross_origin()
def analyze_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    episodeId = Episode.query.with_entities(Episode.id).filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()[0]

    # Retrieve subtitle data
    subUrl = request.form['url']
    subType = request.form['type']
    subResponse = requests.get(subUrl).content

    # Save subtitle data to file in order to load with pysubs2
    subPath = os.path.join(settings.UPLOAD_FOLDER, f'subtitle{subType}')
    with open(subPath, 'wb') as file:
        file.write(subResponse)
    subs = pysubs2.load(subPath)

    # Join subtitles into one string to be processed
    combinedText = ""
    for line in subs:
        combinedText += line.text
        print(line)

    # Get frequencies of words
    resultDict = jpWordExtract(combinedText)
    
    # Add database entries corresponding each word and its frequency of appearance to an episode
    for word in resultDict:
        episodeWord = EpisodeWord(showId, episodeId, word, resultDict[word])
        db.session.add(episodeWord)
    db.session.commit()
    
    return Response(response=json.dumps(resultDict), mimetype='application/json')


# Helper function for /get_episode endpoint to find dictionary data for all retrieved words while grouping words with the same keb or reb together
def retrieveEpisodeWords(vocabToSearch):
    words = []
    for vocab in vocabToSearch:
        # Checks if the word being searched consists of kanji characters only and groups words by kanji if so
        if checkKanji(vocab.word):
            kebFind = Word.query.filter(vocab.word == Word.keb).all()
            sameKeb = []
            if kebFind:
                # Append all words of same kanji representation into one list
                for word in kebFind:
                    sameKeb.append({
                        'id': word.id,
                        'keb': word.keb,
                        'reb': word.reb,
                        'sense': word.sense
                    })
                # Append the grouped list into the overall list of words in the episode
                words.append({
                    "id": vocab.word,
                    "elements": sameKeb
                })
        # If the word only consists of hiragana / katakana, group words by reb instead
        else:
            rebFind = Word.query.filter(and_(vocab.word == Word.reb, Word.keb == None)).all()
            sameReb = []
            if rebFind:
                # Append all words of same reb into one list
                for word in rebFind:
                    sameReb.append({
                        'id': word.id,
                        'keb': word.keb,
                        'reb': word.reb,
                        'sense': word.sense
                    })
                # Append the grouped list into the overall list of words in the episode
                words.append({
                    "id": vocab.word,
                    "elements": sameReb
                })
    
    return words


@anishelf_bp.route('/get_episode', endpoint='/get_episode', methods=['GET'])
@cross_origin()
def get_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))
    offset = int(request.args.get('offset'))

    # Finds episode ID
    episode = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()
    if episode is None:
        return Response(response=json.dumps({ "error": "The requested episode was not found." }), mimetype='application/json')
    
    # Searches for 20 words at a time with the starting word based on the offset, then retrieves dictionary data for those words
    vocabToSearch = EpisodeWord.query.filter(EpisodeWord.episode_id == episode.id).order_by(desc(EpisodeWord.frequency)).limit(20).offset(offset).all()
    finalVocab = retrieveEpisodeWords(vocabToSearch)

    # Determines if there are words before or after current subset of 20 words to indicate if previous or next button should be shown in navbar
    prev = False
    next = False
    if offset != 0:
        prev = True
    if EpisodeWord.query.filter(EpisodeWord.episode_id == episode.id).count() > (offset + 20):
        next = True

    return Response(response=json.dumps({ "vocab": finalVocab, "prev": prev, "next": next}), mimetype='application/json')


# Helper function for /export_episode endpoint to retrieve dictionary data of all words in an episode
def retrieveAllWords(episode_id):
    epId = episode_id

    # Perform a join to look up the dictionary data of all words in the episode
    # When matching word to dictionary entry, the kanji representations should be the same, or it should not have a kanji representation and the readings are the same
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
                and_(EpisodeWord.word == Word.reb,
                Word.keb == None)
            )
        ).filter(EpisodeWord.episode_id == epId) \
        .order_by(desc(EpisodeWord.frequency)) \
        .all()

    # Return all found dictionary data for all words in episode
    return [{
                "id": word.id, 
                "keb": word.keb, 
                "reb": word.reb, 
                "sense": word.sense 
            } for word in finalVocab]


@anishelf_bp.route('/export_episode', endpoint='/export_episode', methods=['GET'])
@cross_origin()
def export_episode():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))

    # Finds episode ID
    episode = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()
    if episode is None:
        return Response(response=json.dumps({ "error": "The requested episode was not found." }), mimetype='application/json')
    
    # Retrieves data for all words in the episode based on the ID
    finalVocab = retrieveAllWords(episode.id)

    return Response(response=json.dumps(finalVocab), mimetype='application/json')


@anishelf_bp.route('/download_subtitles', endpoint='/download_subtitles', methods=['GET'])
@cross_origin()
def download_subtitles():
    showId = int(request.args.get('anilist_id'))
    episodeNo = int(request.args.get('episode'))

    # Find episode ID and corresponding subtitle data
    episode = Episode.query.filter(Episode.episode_no == episodeNo, Episode.show_id == showId).first()
    subtitles = Subtitle.query.filter(Subtitle.episode_id == episode.id).all()

    # Serialize object
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
