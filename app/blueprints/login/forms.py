from wtforms import Form
from wtforms import validators
from wtforms import (IntegerField, 
                     SubmitField, 
                     PasswordField,
                     StringField,
                     TimeField,
                     DateField,
                     validators)
from wtforms.validators import DataRequired, EqualTo
from flask_wtf import FlaskForm
from flask import Flask
import app.blueprints.login.consults as consults
from wtforms.validators import ValidationError
from app.models import(
    Users
)
from app.extensions import Session

class LoginForm(FlaskForm):
    
    user = StringField('Usuario',  
                validators = [DataRequired()]
                )
    
    passw = PasswordField('Contraseña',
                          validators = [DataRequired()]
                          )
    
    submit = SubmitField('Guardar')

    def validate_user(self, user):
        session = Session()
        exists = session.query(Users.user).filter_by(user=user.data).first() is not None
        if not exists:
            raise ValidationError('El usuario no exsite.')
        
# Definir el formulario de registro
class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', 
                           validators=[DataRequired()])
    
    password = PasswordField('Contraseña', 
                             validators=[DataRequired()])
    
    confirm_password = PasswordField('Confirmar contraseña', 
                                     validators=[DataRequired(), 
                                                 EqualTo('password')])
    
    submit = SubmitField('Registrarse')