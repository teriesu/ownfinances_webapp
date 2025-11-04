from . import valoracion
from flask import render_template, redirect, request, flash, session, jsonify, make_response
from flask_login import login_required
from sqlalchemy import (
    text
)
from app.extensions import Session, db, role_required
from app.extensions import db
from app.extensions import limiter

from app.gdrive_management import Gdrive
import app.blueprints.resume.inserts as inserts
import locale

from app.blueprints.valoracion.selection_algorithms import SelectionAlgorithms

import pandas as pd
import numpy as np


@valoracion.route("/", methods = ["GET","POST"])
@login_required
@role_required('admin')
def funcionamiento_base():
    if request.method == 'GET':
        pass

    if request.method == 'POST':
        data = {}
        weights = {}
        minmax = {}

        for key, value in request.form.items():
            if key.startswith('prop'):
                prop, obj = key.split('_')
                if obj not in data:
                    data[obj] = {}
                data[obj][prop] = float(value)
            elif key.startswith('weight'):
                idx = key.replace('weight', '')  # "weight1" → "1"
                weights[f'prop{idx}'] = float(value)
            elif key.startswith('minmax'):
                idx = key.replace('minmax', '')  # "minmax1" → "1"
                minmax[f'prop{idx}'] = value

        # Crear DataFrame principal
        df = pd.DataFrame.from_dict(data, orient='index')

        # Agregar filas con pesos y min/max
        df.loc['weight'] = df.columns.map(lambda col: weights.get(col, None))
        df.loc['minmax'] = df.columns.map(lambda col: minmax.get(col, None))

        sel = SelectionAlgorithms(df)

        resultados = sel.evaluate(methods=None, aggregate=True)

        print("resultados:\n", resultados)

    return render_template('tabla_valoracion.html', title = 'Valoración de gastos')