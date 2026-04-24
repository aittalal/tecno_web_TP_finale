from models import db
from datetime import datetime


class Concert(db.Model):
    """Modèle représentant un concert (à venir ou passé)."""
    __tablename__ = 'concerts'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    artiste = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_concert = db.Column(db.DateTime, nullable=False)
    lieu = db.Column(db.String(200), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=True)   # Pour la météo
    longitude = db.Column(db.Float, nullable=True)  # Pour la météo
    nb_places_total = db.Column(db.Integer, default=100)
    nb_places_restantes = db.Column(db.Integer, default=100)
    prix = db.Column(db.Float, default=0.0)
    image_principale = db.Column(db.String(300), nullable=True)
    avis_redacteur = db.Column(db.Text, nullable=True)  # Avis rédacteur pour les concerts passés
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    # Clé étrangère vers TypeConcert
    type_concert_id = db.Column(db.Integer, db.ForeignKey('types_concerts.id'), nullable=True)

    # Relations
    reservations = db.relationship('Reservation', backref='concert', lazy=True)
    commentaires = db.relationship('Commentaire', backref='concert', lazy=True)
    photos = db.relationship('PhotoConcert', backref='concert', lazy=True, cascade='all, delete-orphan')

    def est_passe(self):
        """Retourne True si le concert est passé."""
        return self.date_concert < datetime.utcnow()

    def places_disponibles(self):
        """Retourne le nombre de places encore disponibles."""
        reservations_total = sum(r.nb_places for r in self.reservations if not r.annulee)
        return self.nb_places_total - reservations_total

    def __repr__(self):
        return f'<Concert {self.titre} - {self.date_concert.strftime("%d/%m/%Y")}>'


class PhotoConcert(db.Model):
    """Photos d'un concert passé."""
    __tablename__ = 'photos_concerts'

    id = db.Column(db.Integer, primary_key=True)
    concert_id = db.Column(db.Integer, db.ForeignKey('concerts.id'), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    legende = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f'<PhotoConcert {self.filename}>'


class Reservation(db.Model):
    """Réservation d'un utilisateur pour un concert."""
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    concert_id = db.Column(db.Integer, db.ForeignKey('concerts.id'), nullable=False)
    nb_places = db.Column(db.Integer, default=1)
    annulee = db.Column(db.Boolean, default=False)
    date_reservation = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Reservation user={self.user_id} concert={self.concert_id} places={self.nb_places}>'
