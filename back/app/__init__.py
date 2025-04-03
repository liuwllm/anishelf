from .config import settings
from flask import Flask
from .api import anishelf_bp
from .database import db
from flask_cors import CORS

# Initialization & config
def create_app():
    app = Flask(__name__)

    CORS(app)

    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL

    db.init_app(app)

    app.register_blueprint(anishelf_bp)

    return app