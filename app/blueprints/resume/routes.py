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
    nombre_archivo = 'Registro movimientos'
    inserts.actualize_db(drive.get_columns_as_dict(nombre_archivo, 'Listas'))
    file_id = drive.get_file_id(nombre_archivo)
    result_wastes = inserts.save_wastes(drive.read_sheet_as_dataframe(nombre_archivo, 'Compras-Gastos'), file_id, 'Compras-Gastos')
    flash(result_wastes[0], result_wastes[1])
    result_incomings = inserts.save_incomings(drive.read_sheet_as_dataframe(nombre_archivo, 'Ingresos'), file_id, 'Ingresos')
    flash(result_incomings[0], result_incomings[1])
    result_investments = inserts.save_investments(drive.read_sheet_as_dataframe(nombre_archivo, 'Inversiones'), file_id, 'Inversiones')
    flash(result_investments[0], result_investments[1])
    
    return redirect('/resume')