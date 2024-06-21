import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Initialization & config

app = Flask(__name__)
CORS(app)

load_dotenv()
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = './'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Models

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    keb = db.Column(db.ARRAY(db.String))
    reb = db.Column(db.ARRAY(db.String))
    sense = db.Column(db.ARRAY(db.String))

    def __init__(self, id, keb=None, reb=None, sense=None):
        self.id = id
        self.keb = keb
        self.reb = reb
        self.sense = sense