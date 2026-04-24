from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models.user import User


class RegistrationForm(FlaskForm):
    """Formulaire d'inscription d'un nouvel utilisateur."""
    username = StringField(
        "Nom d'utilisateur",
        validators=[DataRequired(message="Ce champ est requis."), Length(min=3, max=80)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="Ce champ est requis."), Email(message="Email invalide.")]
    )
    password = PasswordField(
        "Mot de passe",
        validators=[DataRequired(), Length(min=6, message="Minimum 6 caractères.")]
    )
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo('password', message="Les mots de passe ne correspondent pas.")]
    )
    submit = SubmitField("S'inscrire")

    def validate_username(self, username):
        """Vérifie que le nom d'utilisateur n'est pas déjà pris."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")

    def validate_email(self, email):
        """Vérifie que l'email n'est pas déjà enregistré."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Cet email est déjà enregistré.")


class LoginForm(FlaskForm):
    """Formulaire de connexion."""
    email = StringField(
        "Email",
        validators=[DataRequired(message="Ce champ est requis."), Email()]
    )
    password = PasswordField(
        "Mot de passe",
        validators=[DataRequired(message="Ce champ est requis.")]
    )
    remember = BooleanField("Se souvenir de moi")
    submit = SubmitField("Se connecter")
