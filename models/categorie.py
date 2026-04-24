from models import db


class CategorieActualite(db.Model):
    """Catégorie pour les actualités musicales (Jazz, Rock, Electro, etc.)."""
    __tablename__ = 'categories_actualites'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    couleur = db.Column(db.String(20), default='primary')  # Couleur Bootstrap

    # Relations
    actualites = db.relationship('Actualite', backref='categorie', lazy=True)

    def __repr__(self):
        return f'<CategorieActualite {self.nom}>'


class TypeConcert(db.Model):
    """Type de concert (Jazz, Rock, Electro, Classique, etc.)."""
    __tablename__ = 'types_concerts'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)

    # Relations
    concerts = db.relationship('Concert', backref='type_concert', lazy=True)

    def __repr__(self):
        return f'<TypeConcert {self.nom}>'
