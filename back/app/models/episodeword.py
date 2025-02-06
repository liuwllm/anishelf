from ..database import db
from .show import Show
from .episode import Episode

class EpisodeWord(db.Model):
    __tablename__ = 'episodewords'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey(Show.id))
    episode_id = db.Column(db.Integer, db.ForeignKey(Episode.id))
    word = db.Column(db.String, index=True)
    frequency = db.Column(db.Integer)

    def __init__(self, show_id=None, episode_id=None, word=None, frequency=None):
        self.show_id = show_id
        self.episode_id = episode_id
        self.word = word
        self.frequency = frequency