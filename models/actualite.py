from models import db
from datetime import datetime


class Actualite(db.Model):
    """Modèle représentant une actualité musicale."""
    __tablename__ = 'actualites'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(300), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    resume = db.Column(db.String(500), nullable=True)  # Court résumé pour les listes
    image = db.Column(db.String(300), nullable=True)
    date_publication = db.Column(db.DateTime, default=datetime.utcnow)
    date_evenement = db.Column(db.Date, nullable=True)  # Date de l'événement mentionné
    publiee = db.Column(db.Boolean, default=True)

    # Clé étrangère vers CategorieActualite
    categorie_id = db.Column(db.Integer, db.ForeignKey('categories_actualites.id'), nullable=True)

    # Relations
    commentaires = db.relationship('Commentaire', backref='actualite', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Actualite {self.titre}>'
