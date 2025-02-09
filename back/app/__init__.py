from .config import settings
from flask import Flask
from flask_migrate import Migrate
from .api import anishelf_bp
from .database import db

from .models.episode import Episode
from .models.episodeword import EpisodeWord
from .models.show import Show
from .models.subtitle import Subtitle
from .models.word import Word

# Initialization & config
def create_app():
    app = Flask(__name__)

    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL

    db.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        db.create_all()

    app.register_blueprint(anishelf_bp)

    return app