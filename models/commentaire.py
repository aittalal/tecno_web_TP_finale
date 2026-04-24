from models import db
from datetime import datetime


class Commentaire(db.Model):
    """Commentaire posté sur une actualité ou un concert."""
    __tablename__ = 'commentaires'

    id = db.Column(db.Integer, primary_key=True)
    nom_auteur = db.Column(db.String(100), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    approuve = db.Column(db.Boolean, default=True)

    # Clés étrangères (un commentaire appartient soit à une actualité, soit à un concert)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    actualite_id = db.Column(db.Integer, db.ForeignKey('actualites.id'), nullable=True)
    concert_id = db.Column(db.Integer, db.ForeignKey('concerts.id'), nullable=True)

    def __repr__(self):
        return f'<Commentaire by={self.nom_auteur} on={self.date_creation.strftime("%d/%m/%Y")}>'
