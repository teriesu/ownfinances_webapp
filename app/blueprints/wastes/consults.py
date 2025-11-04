from app.models import(
    Gastos,
    CategoriaGasto
)
from sqlalchemy import (
    or_,
    func,
    text
)
from datetime import datetime
from flask import jsonify
from app.extensions import Session


def get_wastes(fecha_inicial, fecha_final):
    session = Session()
    results = text("""
        SELECT 
            gasto_id, 
            cg.categoria, 
            description, 
            monto, 
            fecha
        FROM 
            gastos g
        JOIN 
            categoria_gasto cg ON g.categoria = cg.categoria_id
        WHERE 
            g.fecha >= :fecha_inicial OR :fecha_inicial IS NULL
            AND g.fecha <= :fecha_final OR :fecha_final IS NULL
        ORDER BY 
            fecha DESC;
    """)
    params = {'fecha_inicial': fecha_inicial,
                'fecha_final': fecha_final
              }
    results = session.execute(results, params).fetchall()

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
    results = text("""
        SELECT
            cg.categoria,
            SUM(g.monto)
        FROM
            gastos g
        JOIN
            categoria_gasto cg ON g.categoria = cg.categoria_id
        WHERE
            g.fecha >= :fecha_inicial OR :fecha_inicial IS NULL
            AND g.fecha <= :fecha_final OR :fecha_final IS NULL
        GROUP BY
            cg.categoria;
    """)
    params = {'fecha_inicial': fecha_inicial,
                'fecha_final': fecha_final
              }
    
    results = session.execute(results, params).fetchall()    
    
    session.close()

    data_list = [{
        "Categoria": result[0],
        "Monto": result[1],
        } for result in results]
        
    return jsonify(data_list)