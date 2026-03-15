"""Database configuration. Set environment variables or use a .env file."""
import os

from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "edrine"),
    "database": os.environ.get("DB_NAME", "DISHES_PRICES"),
}
