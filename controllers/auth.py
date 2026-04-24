from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from forms.auth_forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """Inscription d'un nouvel utilisateur."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Création de l'utilisateur
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Compte créé avec succès ! Vous pouvez vous connecter.", "success")
        return redirect(url_for('auth.connexion'))

    return render_template('auth/inscription.html', form=form, title="Inscription")


@auth_bp.route('/connexion', methods=['GET', 'POST'])
def connexion():
    """Connexion d'un utilisateur existant."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f"Bienvenue {user.username} !", "success")
            return redirect(next_page or url_for('main.index'))
        else:
            flash("Email ou mot de passe incorrect.", "danger")

    return render_template('auth/connexion.html', form=form, title="Connexion")


@auth_bp.route('/deconnexion')
@login_required
def deconnexion():
    """Déconnexion de l'utilisateur."""
    logout_user()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for('main.index'))
