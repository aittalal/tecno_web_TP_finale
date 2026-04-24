import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration principale de l'application."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Connexion MariaDB : mysql+pymysql://user:password@host/dbname
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:root@localhost/musiactu'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Dossier pour les photos uploadées
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'img', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    # Clé API OpenWeatherMap (optionnelle)
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
    # Nombre d'éléments affichés sur la page d'accueil
    NB_ACCUEIL_ACTUALITES = 5
    NB_ACCUEIL_CONCERTS = 5
    WTF_CSRF_ENABLED = True
