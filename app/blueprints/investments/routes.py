from . import investments
from flask import render_template, redirect, request, flash, session, jsonify, make_response
from flask_login import login_required
from app.models import(
    Users
)
from app.extensions import limiter, db, role_required
from datetime import datetime

import app.blueprints.investments.consults as Consults

@investments.route("/", methods = ["GET","POST"])
@login_required
@role_required(['admin'])
@limiter.limit('10/minute')
def investments_app():    

    return render_template('investments.html', title = 'Gastos')

@investments.route("/api/table", methods = ["GET","POST"])
@login_required
@role_required(['admin'])
@limiter.limit('10/minute')
def investments_api_table():

    #Capturo fecha inicial y final del resume
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    #Realizo la consulta en la base de datos
    if start_date and end_date:
        inicial = datetime.strptime(start_date, '%Y-%m-%d')
        final = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        final = datetime.now()
        inicial = datetime.now().replace(day=1)

    return Consults.get_investments(inicial, final)

@investments.route("/api/graph", methods = ["GET","POST"])
@login_required
@role_required(['admin'])
@limiter.limit('10/minute')
def investments_api_graph():

    #Capturo fecha inicial y final del resume
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    #Realizo la consulta en la base de datos
    if start_date and end_date:
        inicial = datetime.strptime(start_date, '%Y-%m-%d')
        final = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        final = datetime.now()
        inicial = datetime.now().replace(day=1)

    return Consults.get_graph(inicial, final)