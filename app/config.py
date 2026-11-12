"""
config.py
----------
Application configuration settings.
Update these values according to your local MySQL setup.
"""

import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32)

    # MySQL Database configuration
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "fake_job_detection")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))

    # Paths to trained ML model and vectorizer
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "fake_job_model.pkl")
    VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "models", "tfidf_vectorizer.pkl")
