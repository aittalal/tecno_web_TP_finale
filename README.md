# MUSIACTU 🎵 — Site d'actualité musicale

Site web Flask d'actualité musicale avec gestion de concerts, réservations et administration.

## Stack technique

- **Backend** : Python / Flask (architecture MVC avec Blueprints)
- **Base de données** : MariaDB via Flask-SQLAlchemy
- **Formulaires** : Flask-WTF (validation CSRF)
- **Authentification** : Flask-Login + Flask-Bcrypt
- **CSS** : Bootstrap 5
- **Météo** : OpenWeatherMap API (j ai pas eu le temps pour  faire cette partie)

## Lancer avec GitHub Codespaces

1. Forker ce dépôt
2. Ouvrir dans GitHub Codespaces
3. Le devcontainer installe automatiquement MariaDB + les dépendances
4. Lancer l'application :

```bash
python app.py
```

L'application est accessible sur le port **5000**.

## Installation locale

### Prérequis

- Python 3.11+
- MariaDB ou MySQL

### Installation

```bash
# Cloner le dépôt
git clone <url>
cd univ-flask-astro

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement .env
# Éditer .env avec vos paramètres (DATABASE_URL, SECRET_KEY, etc.)

# Créer la base de données MariaDB
mysql -u root -p -e "CREATE DATABASE musiactu CHARACTER SET utf8mb4;"

# Lancer l'application (crée les tables automatiquement)
python app.py
```

### Compte administrateur par défaut

Au premier lancement, un compte admin est créé automatiquement :

- **Email** : `admin@musiactu.fr`
- **Mot de passe** : `admin1234`


## Structure MVC

```
.
├── app.py                  # Factory Flask, point d'entrée
├── config.py               # Configuration
├── models/                 # MODÈLES (M)
│   ├── user.py             # Utilisateurs
│   ├── concert.py          # Concerts, Réservations, Photos
│   ├── actualite.py        # Actualités musicales
│   ├── categorie.py        # Catégories & Types
│   └── commentaire.py      # Commentaires
├── controllers/            # CONTRÔLEURS (C)
│   ├── main.py             # Page d'accueil
│   ├── auth.py             # Authentification
│   ├── concerts.py         # Concerts + météo
│   ├── actualites.py       # Actualités
│   └── admin.py            # Administration (CRUD)
├── forms/                  # Formulaires Flask-WTF
│   ├── auth_forms.py
│   ├── concert_forms.py
│   ├── actualite_forms.py
│   └── comment_forms.py
├── templates/              # VUES (V)
│   ├── base.html
│   ├── index.html
│   ├── concerts/
│   ├── actualites/
│   ├── auth/
│   ├── admin/
│   └── errors/
└── static/                 # CSS, JS, images
```

## Fonctionnalités

### Public
- **Page d'accueil** : dernières actualités + prochains concerts
- **Concerts à venir** : liste avec filtres (type, ville, dates)
- **Concerts passés** : compte-rendu, photos, avis rédacteur, météo
- **Actualités** : liste par catégorie, détail avec commentaires
- **Inscription / Connexion**
- **Réservation de places** (connecté)
- **Commentaires** sur concerts et actualités

### Administration (`/admin`)
- Dashboard avec statistiques
- CRUD complet : actualités, concerts, catégories, types de concerts
- Upload de photos pour les concerts passés
- Modération des commentaires
- Gestion des utilisateurs (promotion admin)

## Variables d'environnement

| Variable | Description | Défaut |
|---|---|---|
| `SECRET_KEY` | Clé secrète Flask | `dev-secret-key` |
| `DATABASE_URL` | URL MariaDB | `mysql+pymysql://root:root@localhost/musiactu` |
