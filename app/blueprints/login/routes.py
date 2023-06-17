from . import login
from flask import render_template, redirect, request, flash
from app.models import(
    Users
)
from app.extensions import Session
import app.blueprints.login.forms as forms
from passlib.hash import sha256_crypt
from app.extensions import db

@login.route("/", methods = ["GET","POST"])
def login_app():

    form = forms.LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = form.user.data
            password = form.passw.data
            user = Users.query.filter_by(user=user).first()
            if user and sha256_crypt.verify(password, user.password):
                flash('Inicio de sesión exitoso', 'success')
                return redirect('/')
            else:
                flash('Nombre de usuario o contraseña incorrectos', 'danger')


    
    return render_template('login.html', title = 'Login', form=form)

@login.route("/signup", methods = ["GET","POST"])
def register_app():

    form = forms.RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = sha256_crypt.encrypt(form.password.data)

            user = Users(user=username,
                         password=password)
            db.session.add(user)
            db.session.commit()

            flash('Registro exitoso. ¡Inicia sesión ahora!', 'success')
            return redirect('/')

    return render_template('register.html', form=form)
