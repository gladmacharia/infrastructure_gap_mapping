from pathlib import Path
import os
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parents[4]

load_dotenv(base_dir/".env")

GROQ_API = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL","llama-3.3-70b-versatile")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
SSL_MODE = os.getenv("DB_SSLMODE", "require")

database_url = (f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={SSL_MODE}")



