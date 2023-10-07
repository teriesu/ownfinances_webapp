from . import resume
from flask import render_template, redirect, request, flash, session, jsonify, make_response
from flask_security import auth_required
from app.models import(
    Users
)
from app.extensions import Session, db, role_required
from app.extensions import db
from app.extensions import limiter

from app.gdrive_management import Gdrive
import app.blueprints.resume.inserts as inserts

@resume.route("/", methods = ["GET","POST"])
@auth_required('session')
@role_required('admin')
# @limiter.limit('10/minute')
def login_app():

    return render_template('resume.html', title = 'Resumen general')

@resume.route("/actualize_db", methods = ["GET","POST"])
@auth_required('session')
@role_required('admin')
# @limiter.limit('1/minute')
def actualize_info():
    drive = Gdrive()
    inserts.actualize_db(drive.get_columns_as_dict('Registro movimientos', 'Listas'))

    result_wastes = inserts.save_wastes(drive.read_sheet_as_dataframe('Registro movimientos', 'Compras-Gastos'))

    # print(drive.read_sheet_as_dataframe('Registro movimientos', 'Inversiones'))
    # print(drive.read_sheet_as_dataframe('Registro movimientos', 'Ingresos'))
    flash('Funciona perras', 'success')

    return redirect('/resume')