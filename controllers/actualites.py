from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from models.actualite import Actualite
from models.categorie import CategorieActualite
from models.commentaire import Commentaire
from models import db
from forms.comment_forms import CommentaireForm

actualites_bp = Blueprint('actualites', __name__, url_prefix='/actualites')


@actualites_bp.route('/')
def liste():
    """Liste de toutes les actualités publiées, triées par date."""
    actualites = (
        Actualite.query
        .filter_by(publiee=True)
        .order_by(Actualite.date_publication.desc())
        .all()
    )
    categories = CategorieActualite.query.order_by(CategorieActualite.nom).all()
    return render_template(
        'actualites/liste.html',
        actualites=actualites,
        categories=categories,
        categorie_active=None,
        title="Actualités musicales"
    )


@actualites_bp.route('/categorie/<slug>')
def par_categorie(slug):
    """Affiche les actualités filtrées par catégorie (slug)."""
    categorie = CategorieActualite.query.filter_by(slug=slug).first_or_404()
    actualites = (
        Actualite.query
        .filter_by(publiee=True, categorie_id=categorie.id)
        .order_by(Actualite.date_publication.desc())
        .all()
    )
    categories = CategorieActualite.query.order_by(CategorieActualite.nom).all()
    return render_template(
        'actualites/liste.html',
        actualites=actualites,
        categories=categories,
        categorie_active=categorie,
        title=f"Actualités {categorie.nom}"
    )


@actualites_bp.route('/<int:actu_id>')
def detail(actu_id):
    """Affiche le détail d'une actualité et son formulaire de commentaire."""
    actualite = Actualite.query.filter_by(id=actu_id, publiee=True).first_or_404()
    form = CommentaireForm()
    commentaires = (
        Commentaire.query
        .filter_by(actualite_id=actu_id, approuve=True)
        .order_by(Commentaire.date_creation.desc())
        .all()
    )
    return render_template(
        'actualites/detail.html',
        actualite=actualite,
        form=form,
        commentaires=commentaires,
        title=actualite.titre
    )


@actualites_bp.route('/<int:actu_id>/commenter', methods=['POST'])
def commenter(actu_id):
    """Traite la soumission d'un commentaire sur une actualité."""
    actualite = Actualite.query.filter_by(id=actu_id, publiee=True).first_or_404()
    form = CommentaireForm()

    if form.validate_on_submit():
        commentaire = Commentaire(
            nom_auteur=form.nom_auteur.data,
            contenu=form.contenu.data,
            actualite_id=actu_id,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(commentaire)
        db.session.commit()
        flash("Votre commentaire a été posté.", "success")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", "danger")

    return redirect(url_for('actualites.detail', actu_id=actu_id))
