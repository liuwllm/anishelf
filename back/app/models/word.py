from ..database import db

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