from .config import settings
from flask import Flask
from flask_migrate import Migrate
from .api import anishelf_bp
from .database import db

# Initialization & config
def create_app():
    app = Flask(__name__)

    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['UPLOAD_FOLDER'] = './'
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL

    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(anishelf_bp)

    return app