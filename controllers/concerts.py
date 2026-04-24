import os
import requests
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app, abort
)
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db
from models.concert import Concert, Reservation
from models.categorie import TypeConcert
from models.commentaire import Commentaire
from forms.concert_forms import ReservationForm, FiltresConcertsForm
from forms.comment_forms import CommentaireForm

concerts_bp = Blueprint('concerts', __name__, url_prefix='/concerts')


def get_meteo(latitude, longitude, date_concert):
    """
    Récupère la météo prévue pour un concert si celui-ci
    a lieu dans les 15 prochains jours via OpenWeatherMap.
    Retourne None si pas de clé API ou concert trop lointain.
    """
    api_key = current_app.config.get('OPENWEATHER_API_KEY', '')
    if not api_key or not latitude or not longitude:
        return None

    # Météo uniquement si le concert est dans les 15 prochains jours
    maintenant = datetime.utcnow()
    if date_concert < maintenant or (date_concert - maintenant) > timedelta(days=15):
        return None

    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?lat={latitude}&lon={longitude}&appid={api_key}&units=metric&lang=fr"
        )
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get('cod') != '200':
            return None

        # Trouver la prévision la plus proche de la date du concert
        target_ts = date_concert.timestamp()
        meilleure = min(data['list'], key=lambda x: abs(x['dt'] - target_ts))
        return {
            'description': meilleure['weather'][0]['description'].capitalize(),
            'temperature': round(meilleure['main']['temp']),
            'icone': meilleure['weather'][0]['icon'],
        }
    except Exception:
        return None


@concerts_bp.route('/')
def liste():
    """
    Liste des concerts à venir, avec filtres par type, ville, et dates.
    Utilise le formulaire FiltresConcertsForm (sans CSRF).
    """
    form = FiltresConcertsForm(request.args)
    types = TypeConcert.query.order_by(TypeConcert.nom).all()
    form.type_concert.choices = [(0, 'Tous les types')] + [(t.id, t.nom) for t in types]

    query = Concert.query.filter(Concert.date_concert >= datetime.utcnow())

    # Application des filtres
    if form.type_concert.data and form.type_concert.data != 0:
        query = query.filter(Concert.type_concert_id == form.type_concert.data)
    if form.ville.data:
        query = query.filter(Concert.ville.ilike(f'%{form.ville.data}%'))
    if form.date_debut.data:
        query = query.filter(Concert.date_concert >= form.date_debut.data)
    if form.date_fin.data:
        query = query.filter(Concert.date_concert <= form.date_fin.data)

    concerts = query.order_by(Concert.date_concert.asc()).all()

    return render_template(
        'concerts/liste.html',
        concerts=concerts,
        form=form,
        title="Concerts à venir"
    )


@concerts_bp.route('/passes')
def passes():
    """Liste des concerts passés."""
    concerts = (
        Concert.query
        .filter(Concert.date_concert < datetime.utcnow())
        .order_by(Concert.date_concert.desc())
        .all()
    )
    return render_template('concerts/passes.html', concerts=concerts, title="Concerts passés")


@concerts_bp.route('/<int:concert_id>')
def detail(concert_id):
    """
    Détail d'un concert : description, réservation (si à venir),
    météo prévue (si dans les 15 jours), photos et commentaires (si passé).
    """
    concert = Concert.query.get_or_404(concert_id)
    form_reservation = ReservationForm()
    form_commentaire = CommentaireForm()
    meteo = None

    if not concert.est_passe():
        meteo = get_meteo(concert.latitude, concert.longitude, concert.date_concert)

    commentaires = (
        Commentaire.query
        .filter_by(concert_id=concert_id, approuve=True)
        .order_by(Commentaire.date_creation.desc())
        .all()
    )

    return render_template(
        'concerts/detail.html',
        concert=concert,
        form_reservation=form_reservation,
        form_commentaire=form_commentaire,
        commentaires=commentaires,
        meteo=meteo,
        title=concert.titre
    )


@concerts_bp.route('/<int:concert_id>/reserver', methods=['POST'])
@login_required
def reserver(concert_id):
    """Traite la réservation de places pour un concert."""
    concert = Concert.query.get_or_404(concert_id)

    if concert.est_passe():
        flash("Ce concert est terminé, la réservation est impossible.", "warning")
        return redirect(url_for('concerts.detail', concert_id=concert_id))

    form = ReservationForm()
    if form.validate_on_submit():
        nb = form.nb_places.data
        places_dispo = concert.places_disponibles()

        if nb > places_dispo:
            flash(
                f"Seulement {places_dispo} place(s) disponible(s) pour ce concert.",
                "danger"
            )
        else:
            # Vérifier si l'utilisateur a déjà une réservation active
            resa_existante = Reservation.query.filter_by(
                user_id=current_user.id,
                concert_id=concert_id,
                annulee=False
            ).first()

            if resa_existante:
                flash("Vous avez déjà une réservation pour ce concert.", "warning")
            else:
                reservation = Reservation(
                    user_id=current_user.id,
                    concert_id=concert_id,
                    nb_places=nb
                )
                db.session.add(reservation)
                db.session.commit()
                flash(f"Réservation confirmée : {nb} place(s) pour « {concert.titre} ».", "success")

    return redirect(url_for('concerts.detail', concert_id=concert_id))


@concerts_bp.route('/<int:concert_id>/commenter', methods=['POST'])
def commenter(concert_id):
    """Poste un commentaire sur un concert (concert passé)."""
    concert = Concert.query.get_or_404(concert_id)
    form = CommentaireForm()

    if form.validate_on_submit():
        commentaire = Commentaire(
            nom_auteur=form.nom_auteur.data,
            contenu=form.contenu.data,
            concert_id=concert_id,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(commentaire)
        db.session.commit()
        flash("Votre commentaire a été posté.", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", "danger")

    return redirect(url_for('concerts.detail', concert_id=concert_id))


@concerts_bp.route('/<int:concert_id>/annuler-reservation', methods=['POST'])
@login_required
def annuler_reservation(concert_id):
    """Annule la réservation de l'utilisateur pour un concert."""
    reservation = Reservation.query.filter_by(
        user_id=current_user.id,
        concert_id=concert_id,
        annulee=False
    ).first_or_404()

    reservation.annulee = True
    db.session.commit()
    flash("Votre réservation a été annulée.", "info")
    return redirect(url_for('concerts.detail', concert_id=concert_id))
