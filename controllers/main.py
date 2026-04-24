from flask import Blueprint, render_template, current_app
from models.actualite import Actualite
from models.concert import Concert
from datetime import datetime

# Blueprint principal pour la page d'accueil et les pages statiques
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Page d'accueil : affiche les dernières actualités
    et les prochains concerts.
    """
    nb_actu = current_app.config.get('NB_ACCUEIL_ACTUALITES', 5)
    nb_concert = current_app.config.get('NB_ACCUEIL_CONCERTS', 5)

    # Dernières actualités publiées
    dernieres_actualites = (
        Actualite.query
        .filter_by(publiee=True)
        .order_by(Actualite.date_publication.desc())
        .limit(nb_actu)
        .all()
    )

    # Prochains concerts (à venir)
    prochains_concerts = (
        Concert.query
        .filter(Concert.date_concert >= datetime.utcnow())
        .order_by(Concert.date_concert.asc())
        .limit(nb_concert)
        .all()
    )

    return render_template(
        'index.html',
        actualites=dernieres_actualites,
        concerts=prochains_concerts,
        now=datetime.utcnow()
    )
