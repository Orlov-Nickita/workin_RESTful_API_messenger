from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)

MEDIA_ROOT = os.path.join(dir_path, 'media/')

if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)
