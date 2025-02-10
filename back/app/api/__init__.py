from flask import Blueprint

anishelf_bp = Blueprint("anishelf", __name__)

from . import routes