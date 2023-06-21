from app.models import(
    Gastos,
    CategoriaGasto
)
from sqlalchemy import (
    or_,
    func
)
from datetime import datetime
from flask import jsonify
from app.extensions import Session


def get_investments(fecha_inicial, fecha_final):
    session = Session()
    results = session.query(
        Gastos.gasto_id,
        CategoriaGasto.categoria,
        Gastos.description,
        Gastos.monto,
        Gastos.fecha
    ).join(
        CategoriaGasto, Gastos.categoria == CategoriaGasto.categoria_id
    ).filter(
        or_(Gastos.fecha >= fecha_inicial if fecha_inicial is not None else None, fecha_inicial is None),
        or_(Gastos.fecha <= fecha_final if fecha_final is not None else None, fecha_final is None),
    ).all()

    session.close()

    data_list = [{
        "Id": result[0],
        "Categoria": result[1],
        "Descripcion": result[2],
        "Monto": result[3],
        "Fecha": datetime.strftime(result[4], '%d/%m/%Y')
        } for result in results]
        
    return jsonify(data_list)

def get_graph(fecha_inicial, fecha_final):
    session = Session()
    results = session.query(
        CategoriaGasto.categoria,
        func.sum(Gastos.monto),
    ).join(
        CategoriaGasto, Gastos.categoria == CategoriaGasto.categoria_id
    ).filter(
        or_(Gastos.fecha >= fecha_inicial if fecha_inicial is not None else None, fecha_inicial is None),
        or_(Gastos.fecha <= fecha_final if fecha_final is not None else None, fecha_final is None),
    ).group_by(
        CategoriaGasto.categoria
    ).all()
    
    session.close()

    data_list = [{
        "Categoria": result[0],
        "Monto": result[1],
        } for result in results]
        
    return jsonify(data_list)