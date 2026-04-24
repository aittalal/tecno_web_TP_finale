from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class ActualiteForm(FlaskForm):
    """Formulaire d'ajout/modification d'une actualité (admin)."""
    titre = StringField("Titre", validators=[DataRequired(), Length(max=300)])
    resume = StringField("Résumé court", validators=[Optional(), Length(max=500)])
    contenu = TextAreaField("Contenu", validators=[DataRequired()])
    date_evenement = DateField("Date de l'événement", validators=[Optional()])
    categorie_id = SelectField("Catégorie", coerce=int, validators=[Optional()])
    image = FileField(
        "Image d'illustration",
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], "Images uniquement !"), Optional()]
    )
    publiee = BooleanField("Publier immédiatement", default=True)
    submit = SubmitField("Enregistrer")


class CategorieActualiteForm(FlaskForm):
    """Formulaire d'ajout/modification d'une catégorie d'actualités."""
    nom = StringField("Nom", validators=[DataRequired(), Length(max=80)])
    slug = StringField("Slug (URL)", validators=[DataRequired(), Length(max=80)])
    couleur = SelectField(
        "Couleur Bootstrap",
        choices=[
            ('primary', 'Bleu (primary)'),
            ('success', 'Vert (success)'),
            ('danger', 'Rouge (danger)'),
            ('warning', 'Jaune (warning)'),
            ('info', 'Cyan (info)'),
            ('dark', 'Sombre (dark)'),
        ]
    )
    submit = SubmitField("Enregistrer")
