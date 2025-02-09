import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
JIMAKU_KEY = os.getenv('JIMAKU_KEY')
UPLOAD_FOLDER = "./"