import os
import uuid
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, current_app, abort
)
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from models import db
from models.actualite import Actualite
from models.concert import Concert, PhotoConcert
from models.categorie import CategorieActualite, TypeConcert
from models.commentaire import Commentaire
from models.user import User
from forms.concert_forms import ConcertForm
from forms.actualite_forms import ActualiteForm, CategorieActualiteForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


def admin_required(f):
    """Décorateur qui vérifie que l'utilisateur est administrateur."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def save_image(file_field):
    """
    Sauvegarde un fichier image uploadé dans le dossier UPLOAD_FOLDER.
    Retourne le nom de fichier unique généré, ou None si pas de fichier.
    """
    if not file_field or not file_field.filename:
        return None
    ext = file_field.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file_field.save(os.path.join(upload_folder, filename))
    return filename


# ─── Dashboard ────────────────────────────────────────────────────────────────

@admin_bp.route('/')
@admin_required
def dashboard():
    """Tableau de bord de l'administration."""
    stats = {
        'nb_concerts': Concert.query.count(),
        'nb_actualites': Actualite.query.count(),
        'nb_users': User.query.count(),
        'nb_commentaires': Commentaire.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats, title="Administration")


# ─── Gestion des Actualités ───────────────────────────────────────────────────

@admin_bp.route('/actualites')
@admin_required
def actualites():
    """Liste toutes les actualités."""
    liste = Actualite.query.order_by(Actualite.date_publication.desc()).all()
    return render_template('admin/actualites.html', actualites=liste, title="Gérer les actualités")


@admin_bp.route('/actualites/ajouter', methods=['GET', 'POST'])
@admin_required
def ajouter_actualite():
    """Ajoute une nouvelle actualité."""
    form = ActualiteForm()
    categories = CategorieActualite.query.order_by(CategorieActualite.nom).all()
    form.categorie_id.choices = [(0, '— Aucune —')] + [(c.id, c.nom) for c in categories]

    if form.validate_on_submit():
        image_name = save_image(form.image.data)
        actu = Actualite(
            titre=form.titre.data,
            resume=form.resume.data,
            contenu=form.contenu.data,
            date_evenement=form.date_evenement.data,
            categorie_id=form.categorie_id.data or None,
            image=image_name,
            publiee=form.publiee.data
        )
        db.session.add(actu)
        db.session.commit()
        flash("Actualité ajoutée avec succès.", "success")
        return redirect(url_for('admin.actualites'))

    return render_template('admin/form_actualite.html', form=form, title="Ajouter une actualité")


@admin_bp.route('/actualites/modifier/<int:actu_id>', methods=['GET', 'POST'])
@admin_required
def modifier_actualite(actu_id):
    """Modifie une actualité existante."""
    actu = Actualite.query.get_or_404(actu_id)
    form = ActualiteForm(obj=actu)
    categories = CategorieActualite.query.order_by(CategorieActualite.nom).all()
    form.categorie_id.choices = [(0, '— Aucune —')] + [(c.id, c.nom) for c in categories]

    if form.validate_on_submit():
        actu.titre = form.titre.data
        actu.resume = form.resume.data
        actu.contenu = form.contenu.data
        actu.date_evenement = form.date_evenement.data
        actu.categorie_id = form.categorie_id.data or None
        actu.publiee = form.publiee.data
        new_image = save_image(form.image.data)
        if new_image:
            actu.image = new_image
        db.session.commit()
        flash("Actualité modifiée.", "success")
        return redirect(url_for('admin.actualites'))

    return render_template('admin/form_actualite.html', form=form, actu=actu, title="Modifier une actualité")


@admin_bp.route('/actualites/supprimer/<int:actu_id>', methods=['POST'])
@admin_required
def supprimer_actualite(actu_id):
    """Supprime une actualité."""
    actu = Actualite.query.get_or_404(actu_id)
    db.session.delete(actu)
    db.session.commit()
    flash("Actualité supprimée.", "info")
    return redirect(url_for('admin.actualites'))


# ─── Gestion des Catégories ───────────────────────────────────────────────────

@admin_bp.route('/categories')
@admin_required
def categories():
    """Liste toutes les catégories d'actualités."""
    liste = CategorieActualite.query.order_by(CategorieActualite.nom).all()
    form = CategorieActualiteForm()
    return render_template('admin/categories.html', categories=liste, form=form, title="Catégories")


@admin_bp.route('/categories/ajouter', methods=['POST'])
@admin_required
def ajouter_categorie():
    """Ajoute une catégorie d'actualité."""
    form = CategorieActualiteForm()
    if form.validate_on_submit():
        cat = CategorieActualite(
            nom=form.nom.data,
            slug=form.slug.data,
            couleur=form.couleur.data
        )
        db.session.add(cat)
        db.session.commit()
        flash("Catégorie ajoutée.", "success")
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/supprimer/<int:cat_id>', methods=['POST'])
@admin_required
def supprimer_categorie(cat_id):
    """Supprime une catégorie."""
    cat = CategorieActualite.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash("Catégorie supprimée.", "info")
    return redirect(url_for('admin.categories'))


# ─── Gestion des Concerts ─────────────────────────────────────────────────────

@admin_bp.route('/concerts')
@admin_required
def concerts():
    """Liste tous les concerts."""
    liste = Concert.query.order_by(Concert.date_concert.desc()).all()
    return render_template('admin/concerts.html', concerts=liste, title="Gérer les concerts")


@admin_bp.route('/concerts/ajouter', methods=['GET', 'POST'])
@admin_required
def ajouter_concert():
    """Ajoute un nouveau concert."""
    form = ConcertForm()
    types = TypeConcert.query.order_by(TypeConcert.nom).all()
    form.type_concert_id.choices = [(0, '— Aucun —')] + [(t.id, t.nom) for t in types]

    if form.validate_on_submit():
        image_name = save_image(form.image_principale.data)
        concert = Concert(
            titre=form.titre.data,
            artiste=form.artiste.data,
            description=form.description.data,
            date_concert=form.date_concert.data,
            lieu=form.lieu.data,
            ville=form.ville.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            nb_places_total=form.nb_places_total.data,
            nb_places_restantes=form.nb_places_total.data,
            prix=form.prix.data or 0.0,
            type_concert_id=form.type_concert_id.data or None,
            image_principale=image_name,
            avis_redacteur=form.avis_redacteur.data
        )
        db.session.add(concert)
        db.session.commit()
        flash("Concert ajouté avec succès.", "success")
        return redirect(url_for('admin.concerts'))

    return render_template('admin/form_concert.html', form=form, title="Ajouter un concert")


@admin_bp.route('/concerts/modifier/<int:concert_id>', methods=['GET', 'POST'])
@admin_required
def modifier_concert(concert_id):
    """Modifie un concert existant."""
    concert = Concert.query.get_or_404(concert_id)
    form = ConcertForm(obj=concert)
    types = TypeConcert.query.order_by(TypeConcert.nom).all()
    form.type_concert_id.choices = [(0, '— Aucun —')] + [(t.id, t.nom) for t in types]

    if form.validate_on_submit():
        concert.titre = form.titre.data
        concert.artiste = form.artiste.data
        concert.description = form.description.data
        concert.date_concert = form.date_concert.data
        concert.lieu = form.lieu.data
        concert.ville = form.ville.data
        concert.latitude = form.latitude.data
        concert.longitude = form.longitude.data
        concert.nb_places_total = form.nb_places_total.data
        concert.prix = form.prix.data or 0.0
        concert.type_concert_id = form.type_concert_id.data or None
        concert.avis_redacteur = form.avis_redacteur.data
        new_image = save_image(form.image_principale.data)
        if new_image:
            concert.image_principale = new_image
        db.session.commit()
        flash("Concert modifié.", "success")
        return redirect(url_for('admin.concerts'))

    return render_template('admin/form_concert.html', form=form, concert=concert, title="Modifier un concert")


@admin_bp.route('/concerts/supprimer/<int:concert_id>', methods=['POST'])
@admin_required
def supprimer_concert(concert_id):
    """Supprime un concert et ses données associées."""
    concert = Concert.query.get_or_404(concert_id)
    db.session.delete(concert)
    db.session.commit()
    flash("Concert supprimé.", "info")
    return redirect(url_for('admin.concerts'))


@admin_bp.route('/concerts/<int:concert_id>/photos', methods=['POST'])
@admin_required
def ajouter_photo(concert_id):
    """Ajoute une ou plusieurs photos à un concert passé."""
    concert = Concert.query.get_or_404(concert_id)
    files = request.files.getlist('photos')
    for f in files:
        filename = save_image(f)
        if filename:
            photo = PhotoConcert(concert_id=concert_id, filename=filename)
            db.session.add(photo)
    db.session.commit()
    flash("Photos ajoutées.", "success")
    return redirect(url_for('admin.modifier_concert', concert_id=concert_id))


# ─── Gestion des Types de Concert ────────────────────────────────────────────

@admin_bp.route('/types-concerts')
@admin_required
def types_concerts():
    """Liste les types de concerts."""
    types = TypeConcert.query.order_by(TypeConcert.nom).all()
    return render_template('admin/types_concerts.html', types=types, title="Types de concerts")


@admin_bp.route('/types-concerts/ajouter', methods=['POST'])
@admin_required
def ajouter_type_concert():
    """Ajoute un type de concert."""
    nom = request.form.get('nom', '').strip()
    slug = request.form.get('slug', '').strip()
    if nom and slug:
        t = TypeConcert(nom=nom, slug=slug)
        db.session.add(t)
        db.session.commit()
        flash("Type de concert ajouté.", "success")
    return redirect(url_for('admin.types_concerts'))


@admin_bp.route('/types-concerts/supprimer/<int:type_id>', methods=['POST'])
@admin_required
def supprimer_type_concert(type_id):
    """Supprime un type de concert."""
    t = TypeConcert.query.get_or_404(type_id)
    db.session.delete(t)
    db.session.commit()
    flash("Type supprimé.", "info")
    return redirect(url_for('admin.types_concerts'))


# ─── Gestion des commentaires ─────────────────────────────────────────────────

@admin_bp.route('/commentaires')
@admin_required
def commentaires():
    """Liste tous les commentaires pour modération."""
    liste = Commentaire.query.order_by(Commentaire.date_creation.desc()).all()
    return render_template('admin/commentaires.html', commentaires=liste, title="Commentaires")


@admin_bp.route('/commentaires/supprimer/<int:comm_id>', methods=['POST'])
@admin_required
def supprimer_commentaire(comm_id):
    """Supprime un commentaire."""
    comm = Commentaire.query.get_or_404(comm_id)
    db.session.delete(comm)
    db.session.commit()
    flash("Commentaire supprimé.", "info")
    return redirect(url_for('admin.commentaires'))


# ─── Gestion des utilisateurs ────────────────────────────────────────────────

@admin_bp.route('/utilisateurs')
@admin_required
def utilisateurs():
    """Liste tous les utilisateurs."""
    liste = User.query.order_by(User.date_inscription.desc()).all()
    return render_template('admin/utilisateurs.html', users=liste, title="Utilisateurs")


@admin_bp.route('/utilisateurs/promouvoir/<int:user_id>', methods=['POST'])
@admin_required
def promouvoir_admin(user_id):
    """Donne le rôle admin à un utilisateur."""
    user = User.query.get_or_404(user_id)
    user.role = 'admin'
    db.session.commit()
    flash(f"{user.username} est maintenant administrateur.", "success")
    return redirect(url_for('admin.utilisateurs'))
