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
from app.services.exchange_rate_service import ExchangeRateService

def get_incomings(fecha_inicial, fecha_final):
    session = Session()
    results = text("""
        SELECT 
            ingreso_id, 
            ci.categoria_ingreso, 
            i.description, 
            i.monto, 
            i.fecha
            -- d.divisa,
            -- d.abreviacion,
            -- d.simbolo
        FROM 
            ingresos i
        JOIN 
            categoria_ingreso ci ON i.categoria = ci.categoria_ingreso_id
        -- JOIN
            -- divisas d ON g.divisa = d.divisa_id
        WHERE 
            i.fecha >= :fecha_inicial OR :fecha_inicial IS NULL
            AND i.fecha <= :fecha_final OR :fecha_final IS NULL
        ORDER BY 
            i.fecha DESC;
    """)
    params = {'fecha_inicial': fecha_inicial,
                'fecha_final': fecha_final
              }
    results = session.execute(results, params).fetchall()

    session.close()

    data_list = []
    for result in results:
        # original_amount = result[3]
        # transaction_date = result[4]  # Fecha de la transacción
        # currency_abbrev = result[6]
        
        # Convertir a COP si se solicita, usando la fecha de la transacción
        # if convert_currency:
        #     amount_in_cop = convert_to_cop(original_amount, currency_abbrev, transaction_date)
        #     display_amount = amount_in_cop
        #     currency_display = "COP"
        # else:
        #     display_amount = original_amount
        #     currency_display = currency_abbrev
        
        data_list.append({
            "Id": result[0],
            "Categoria": result[1],
            "Descripcion": result[2],
            "Monto": result[3],
            "Fecha": result[4],
        })
    
    print(data_list)
    return jsonify(data_list)
