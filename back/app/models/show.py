from ..database import db

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, index=True)
    episodes = db.relationship('Episode', backref='show')
    episodewords = db.relationship('EpisodeWord', backref='show')

    def __init__(self, id):
        self.id = id