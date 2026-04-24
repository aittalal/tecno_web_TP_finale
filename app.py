"""
app.py — Point d'entrée principal de l'application MUSIACTU.
Architecture MVC avec Flask Blueprints.
"""
# --- Ajoute cet import en haut du fichier ---
from flask_wtf.csrf import CSRFProtect

# --- Initialise l'objet ici ---
csrf = CSRFProtect()
from flask import Flask
from config import Config
from models import db, login_manager, bcrypt, migrate
from models.categorie import CategorieActualite


def create_app(config_class=Config):
    """
    Factory function Flask : crée et configure l'application.
    Enregistre les extensions et les blueprints (contrôleurs).
    """

    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Initialisation des extensions ──────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    # --- AJOUTE CETTE LIGNE ICI ---
    csrf.init_app(app)

    # Configuration Flask-Login
    login_manager.login_view = 'auth.connexion'
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = "warning"

    # ── Chargement de l'utilisateur (Flask-Login) ──────────────────────────
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        """Charge l'utilisateur depuis la base de données par son ID."""
        return User.query.get(int(user_id))

    # ── Enregistrement des blueprints (contrôleurs MVC) ───────────────────
    from controllers.main import main_bp
    from controllers.auth import auth_bp
    from controllers.concerts import concerts_bp
    from controllers.actualites import actualites_bp
    from controllers.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(concerts_bp)
    app.register_blueprint(actualites_bp)
    app.register_blueprint(admin_bp)

    # ── Injection de contexte global dans les templates ────────────────────
    @app.context_processor
    def inject_globals():
        """
        Injecte les catégories d'actualités et l'utilisateur courant
        dans tous les templates Jinja2.
        """
        def get_categories():
            try:
                return CategorieActualite.query.order_by(CategorieActualite.nom).all()
            except Exception:
                return []
        return dict(get_categories=get_categories)

    # ── Gestionnaires d'erreurs ────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    # ── Création des tables et données initiales ───────────────────────────
    with app.app_context():
        db.create_all()
        _seed_initial_data()

    return app


def _seed_initial_data():
    """
    Insère des données initiales si la base est vide :
    - catégories d'actualités par défaut
    - types de concerts
    - compte administrateur par défaut
    """
    from models.categorie import CategorieActualite, TypeConcert
    from models.user import User

    # Catégories d'actualités
    if CategorieActualite.query.count() == 0:
        categories = [
            CategorieActualite(nom='Jazz', slug='jazz', couleur='warning'),
            CategorieActualite(nom='Rock', slug='rock', couleur='danger'),
            CategorieActualite(nom='Électro', slug='electro', couleur='info'),
            CategorieActualite(nom='Classique', slug='classique', couleur='secondary'),
            CategorieActualite(nom='Pop', slug='pop', couleur='primary'),
            CategorieActualite(nom='Hip-Hop', slug='hip-hop', couleur='dark'),
        ]
        db.session.bulk_save_objects(categories)
        db.session.commit()

    # Types de concerts
    if TypeConcert.query.count() == 0:
        types = [
            TypeConcert(nom='Jazz', slug='jazz'),
            TypeConcert(nom='Rock', slug='rock'),
            TypeConcert(nom='Électro', slug='electro'),
            TypeConcert(nom='Classique', slug='classique'),
            TypeConcert(nom='Festivals', slug='festivals'),
        ]
        db.session.bulk_save_objects(types)
        db.session.commit()

    # Compte admin par défaut
    if User.query.filter_by(role='admin').count() == 0:
        admin = User(username='admin', email='admin@musiactu.fr', role='admin')
        admin.set_password('admin1234')
        db.session.add(admin)
        db.session.commit()
        print("[MUSIACTU] Compte admin créé : admin@musiactu.fr / admin1234")


# ── Point d'entrée ──────────────────────────────────────────────────────────
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)