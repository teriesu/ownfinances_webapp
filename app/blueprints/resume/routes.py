from . import resume
from flask import render_template, redirect, request, flash, session, jsonify, make_response
from flask_security import auth_required
from sqlalchemy import (
    text
)
from app.extensions import Session, db, role_required
from app.extensions import db
from app.extensions import limiter

from app.gdrive_management import Gdrive
import app.blueprints.resume.inserts as inserts
import locale

try:
    locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')  # Ajusta según el sistema, puede ser 'es_CO.utf8' en algunos sistemas
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # Usar el locale por defecto del sistema si no está disponible es_CO.UTF-8

@resume.route("/", methods = ["GET","POST"])
@auth_required('session')
@role_required('admin')
# @limiter.limit('10/minute')
def login_app():
    session = Session()

    consult = text("""
        SELECT
            patrimonio, 
            liquidez, 
            UPPER(description)
        FROM
            historical_money
        ORDER BY
            fecha DESC;
        """)
    results = session.execute(consult).fetchone()
    session.close()

    patrimonio_actual = locale.currency(results[0], grouping=True)
    liquidez_actual = locale.currency(results[1], grouping=True)
    ultimo_movimiento = results[2]

    return render_template('resume.html', title = 'Resumen general', patrimonio = patrimonio_actual, liquidez = liquidez_actual, ultimo_movimiento = ultimo_movimiento)

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