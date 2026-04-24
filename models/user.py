from flask_login import UserMixin
from models import db, bcrypt


class User(db.Model, UserMixin):
    """Modèle utilisateur pour l'authentification et les réservations."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # Rôle : 'user' ou 'admin'
    role = db.Column(db.String(20), default='user', nullable=False)
    date_inscription = db.Column(db.DateTime, default=db.func.now())

    # Relations
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    commentaires = db.relationship('Commentaire', backref='user', lazy=True)

    def set_password(self, password):
        """Hashe et stocke le mot de passe."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Vérifie le mot de passe en clair par rapport au hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Retourne True si l'utilisateur est administrateur."""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'
