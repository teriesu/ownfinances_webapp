from . import login
from flask import render_template, redirect, request, flash, session, jsonify
from app.models import(
    Users, Role
)
from app.extensions import Session
import app.blueprints.login.forms as forms
from passlib.hash import sha256_crypt
from app.extensions import db

from app.extensions import limiter, login_manager

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import uuid

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
                # Ensure fs_uniquifier is set
                if not user.fs_uniquifier:
                    user.fs_uniquifier = str(uuid.uuid4())
                    db.session.commit()
                    
                # Login with flask-login and set remember=True for persistent sessions
                login_user(user, remember=True)
                
                # Ensure session is marked as permanent
                session.permanent = True
                
                # Set additional session variables
                session['logged_in'] = True
                session['user_id'] = user.id
                session.modified = True
                
                # Limpiar y establecer una nueva sesión
                session.pop('_flashes', None)
                
                # Redirect to next page if specified, otherwise to /resume
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
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
                         password=password,
                         fs_uniquifier=str(uuid.uuid4()))
            
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

@login.route('/user_status')
def user_status():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user_id': current_user.id,
            'username': current_user.user,
            'fs_uniquifier': current_user.fs_uniquifier,
            'roles': [role.name for role in current_user.roles],
            'active': current_user.active
        })
    else:
        return jsonify({
            'authenticated': False
        })

@login.route('/debug')
def debug_route():
    from flask_login import current_user
    
    if current_user.is_authenticated:
        user_data = {
            'authenticated': True,
            'user_id': current_user.id,
            'username': current_user.user,
            'fs_uniquifier': current_user.fs_uniquifier,
            'roles': [role.name for role in current_user.roles]
        }
        return render_template('debug.html', user_data=user_data)
    else:
        return render_template('debug.html', user_data={'authenticated': False})