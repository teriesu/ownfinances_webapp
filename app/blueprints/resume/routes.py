from . import resume
from flask import render_template, redirect, request, flash, session, jsonify, make_response
from flask_login import login_required
from sqlalchemy import (
    text
)
from app.extensions import Session, db, role_required
from app.extensions import db
from app.extensions import limiter

from app.services.gdrive_management import Gdrive
import app.blueprints.resume.inserts as inserts
import app.blueprints.resume.consults as consults
from app.services.exchange_rate_service import ExchangeRateService
from app.general_funcions import divisa_string_to_id
from datetime import date
import locale
from app.blueprints.resume.auxiliar_functions import calculate_total_liquidity

# Try to set Spanish Colombia locale, with fallbacks
locale_options = ['es_CO.UTF-8', 'es_CO.utf8', 'es_ES.UTF-8', 'C.UTF-8', '']
locale_set = False

for loc in locale_options:
    try:
        locale.setlocale(locale.LC_ALL, loc)
        locale_set = True
        print(f"Locale set to: {loc}")
        break
    except locale.Error:
        continue

if not locale_set:
    print("Warning: Could not set preferred locale, using default")

def safe_currency_format(value, symbol='$', grouping=True):
    """
    Safely format currency value with fallback if locale doesn't support currency formatting
    """
    try:
        return locale.currency(value, grouping=grouping, symbol=True)
    except ValueError:
        # Fallback: manual formatting
        if grouping:
            formatted = f"{value:,.0f}"
        else:
            formatted = f"{value:.0f}"
        return f"{symbol}{formatted}"

@resume.route("/", methods = ["GET","POST"])
@login_required
@role_required('admin')
# @limiter.limit('10/minute')
def login_app():
    session_db = Session()

    # Obtener patrimonio de la tabla histórica (si aún es relevante)
    consult = text("""
        SELECT
            patrimonio, 
            UPPER(description)
        FROM
            historical_money
        ORDER BY
            fecha DESC
        LIMIT 1;
        """)
    results = session_db.execute(consult).fetchone()
    session_db.close()

    # Calcular liquidez actual basada en saldos de cuentas
    liquidez_total_cop = calculate_total_liquidity()

    patrimonio_actual = safe_currency_format(results[0] if results else 0)
    liquidez_actual = safe_currency_format(liquidez_total_cop)
    ultimo_movimiento = results[1] if results else "Sin movimientos"

    return render_template('resume.html', title = 'Resumen general', patrimonio = patrimonio_actual, liquidez = liquidez_actual, ultimo_movimiento = ultimo_movimiento)

@resume.route("/actualize_db", methods = ["GET","POST"])
@login_required
@role_required('admin')
# @limiter.limit('1/minute')
def actualize_info():
    drive = Gdrive()
    nombre_archivo = 'Registro movimientos'
    inserts.actualize_db(drive.get_columns_as_dict(nombre_archivo, 'Listas'))
    file_id = drive.get_file_id(nombre_archivo)
    # result_wastes = inserts.save_wastes(drive.read_sheet_as_dataframe(nombre_archivo, 'Compras-Gastos'), file_id, 'Compras-Gastos')
    # flash(result_wastes[0], result_wastes[1])
    result_incomings = inserts.save_incomings(drive.read_sheet_as_dataframe(nombre_archivo, 'Ingresos'), file_id, 'Ingresos')
    flash(result_incomings[0], result_incomings[1])
    # result_investments = inserts.save_investments(drive.read_sheet_as_dataframe(nombre_archivo, 'Inversiones'), file_id, 'Inversiones')
    # flash(result_investments[0], result_investments[1])
    
    return redirect('/resume')

    
@resume.route("/expenses_by_category", methods=["GET"])
@login_required
@role_required('admin')
def expenses_by_category():

    session_db = Session()

    query = text("""
        SELECT
            c.categoria,
            SUM(e.monto) AS total
        FROM
            gastos e
        JOIN
            categoria_gasto c ON e.categoria = c.categoria_id
        WHERE
            e.fecha >= DATE_TRUNC('month', CURRENT_DATE)
            AND e.fecha < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
        GROUP BY
            c.categoria
        ORDER BY
            total DESC;
    """)
    results = session_db.execute(query).fetchall()
    session_db.close()


    labels = [row[0] for row in results]
    values = [float(row[1]) for row in results]

    return jsonify({'labels': labels, 'values': values})