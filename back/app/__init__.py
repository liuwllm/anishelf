from .config import settings
from flask import Flask
from flask_migrate import Migrate
from .api import anishelf_bp
from .database import db
from flask_cors import CORS

from .models.episode import Episode
from .models.episodeword import EpisodeWord
from .models.show import Show
from .models.subtitle import Subtitle
from .models.word import Word

# Initialization & config
def create_app():
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL

    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(anishelf_bp)

    return app