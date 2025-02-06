from ..database import db
from .episode import Episode

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