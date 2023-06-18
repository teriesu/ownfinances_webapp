from . import login
from flask import render_template, redirect, request, flash, session
from app.models import(
    Users, Role
)
from app.extensions import Session
import app.blueprints.login.forms as forms
from passlib.hash import sha256_crypt
from app.extensions import db

from app.extensions import limiter, login_manager

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

@login.route("/", methods = ["GET","POST"])
@limiter.limit('10/minute')
def login_app():
    form = forms.LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = form.user.data
            password = form.passw.data
            user = Users.query.filter_by(user=user).first()
            if user and sha256_crypt.verify(password, user.password):
                login_user(user)
                # token = security.create_token(user)
                flash('Inicio de sesión exitoso', 'success')

                # Establecer la sesión y rotar las cookies
                session['logged_in'] = True
                session.modified = True
                session.permanent = True

                # Limpiar y establecer una nueva sesión
                session.pop('_flashes', None)
                return redirect('/resume')
            else:
                flash('Nombre de usuario o contraseña incorrectos', 'danger')

    return render_template('login.html', form=form)

@login.route("/signup", methods = ["GET","POST"])
@limiter.limit('2/minute')
def register_app():

    form = forms.RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt(form.password.data)

            user = Users(user=username,
                         email=email,
                         password=password)
            
            # admin_role = Role.query.filter_by(name='admin').first()
            # if admin_role:
            #     # Asigna el rol 'admin' al usuario
            #     user.roles.append(admin_role)
            db.session.add(user)
            db.session.commit()

            flash('Registro exitoso. ¡Inicia sesión ahora!', 'success')
            return redirect('/')

    return render_template('register.html', form=form)

@login.route('/logout')
def logout():
    logout_user()
    return redirect('/')