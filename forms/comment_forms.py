from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class CommentaireForm(FlaskForm):
    """Formulaire pour poster un commentaire."""
    nom_auteur = StringField(
        "Nom",
        validators=[DataRequired(message="Votre nom est requis."), Length(max=100)]
    )
    contenu = TextAreaField(
        "Mon commentaire",
        validators=[DataRequired(message="Le commentaire ne peut pas être vide."), Length(min=5)]
    )
    submit = SubmitField("Envoyer")
