from flask import Blueprint
from flask_cors import CORS

anishelf_bp = Blueprint("anishelf", __name__)

CORS(anishelf_bp)

from . import routes