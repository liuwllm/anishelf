from ..database import db
from .show import Show

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