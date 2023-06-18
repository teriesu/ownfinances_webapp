from . import resume
from flask import render_template, redirect, request, flash, session, jsonify, make_response
from flask_security import auth_required
from app.models import(
    Users
)
from app.extensions import Session, db, role_required
from app.extensions import db


from app.extensions import limiter

@resume.route("/", methods = ["GET","POST"])
@auth_required('session')
@role_required('admin')
@limiter.limit('10/minute')
def login_app():

    return render_template('resume.html', title = 'Resumen general')