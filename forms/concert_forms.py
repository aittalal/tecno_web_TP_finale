from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, IntegerField, FloatField,
    DateTimeLocalField, SubmitField, SelectField
)
from wtforms.validators import DataRequired, NumberRange, Optional, Length


class ConcertForm(FlaskForm):
    """Formulaire d'ajout/modification d'un concert (admin)."""
    titre = StringField("Titre", validators=[DataRequired(), Length(max=200)])
    artiste = StringField("Artiste", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[Optional()])
    date_concert = DateTimeLocalField(
        "Date et heure du concert",
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()]
    )
    lieu = StringField("Lieu / Salle", validators=[DataRequired(), Length(max=200)])
    ville = StringField("Ville", validators=[DataRequired(), Length(max=100)])
    latitude = FloatField("Latitude (pour météo)", validators=[Optional()])
    longitude = FloatField("Longitude (pour météo)", validators=[Optional()])
    nb_places_total = IntegerField(
        "Nombre de places total",
        validators=[DataRequired(), NumberRange(min=1)],
        default=100
    )
    prix = FloatField("Prix (€)", validators=[Optional(), NumberRange(min=0)], default=0.0)
    type_concert_id = SelectField("Type de concert", coerce=int, validators=[Optional()])
    image_principale = FileField(
        "Image principale",
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], "Images uniquement !"), Optional()]
    )
    avis_redacteur = TextAreaField("Avis du rédacteur en chef", validators=[Optional()])
    submit = SubmitField("Enregistrer")


class ReservationForm(FlaskForm):
    """Formulaire de réservation pour un concert."""
    nb_places = IntegerField(
        "Nombre de places",
        validators=[DataRequired(), NumberRange(min=1, max=10, message="Entre 1 et 10 places.")],
        default=1
    )
    submit = SubmitField("Réserver")


class FiltresConcertsForm(FlaskForm):
    """Formulaire de filtrage de la liste des concerts."""
    type_concert = SelectField("Type", coerce=int, validators=[Optional()])
    ville = StringField("Ville", validators=[Optional()])
    date_debut = DateTimeLocalField("Du", format='%Y-%m-%dT%H:%M', validators=[Optional()])
    date_fin = DateTimeLocalField("Au", format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField("Filtrer")

    class Meta:
        csrf = False  # Pas de CSRF sur le formulaire de filtre (GET)
