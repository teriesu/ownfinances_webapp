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


def get_exchange_rates():
    """
    DEPRECATED: Usar ExchangeRateService en su lugar
    Mantener por compatibilidad temporal
    """
    return {
        'COP': 1.0,      # Base currency
        'USD': 4200.0,   # 1 USD = 4200 COP (ejemplo)
        'EUR': 4600.0,   # 1 EUR = 4600 COP (ejemplo)
        'GBP': 5300.0,   # 1 GBP = 5300 COP (ejemplo)
        'JPY': 28.0,     # 1 JPY = 28 COP (ejemplo)
        'CAD': 3100.0,   # 1 CAD = 3100 COP (ejemplo)
    }

def convert_to_cop(amount, currency_abbreviation, transaction_date=None):
    """
    Convierte un monto de cualquier divisa a COP usando tasas dinámicas
    Args:
        amount: Monto en la divisa original
        currency_abbreviation: Abreviación de la divisa (COP, USD, EUR, etc.)
        transaction_date: Fecha de la transacción (date object o string)
    Returns:
        float: Monto convertido a COP
    """
    if currency_abbreviation == 'COP':
        return amount
    
    try:
        exchange_service = ExchangeRateService()
        return exchange_service.convert_amount(
            amount, 
            currency_abbreviation, 
            'COP', 
            transaction_date
        )
    except Exception as e:
        print(f"Error converting {currency_abbreviation} to COP: {e}")
        # Fallback a tasas estáticas
        exchange_rates = get_exchange_rates()
        if currency_abbreviation in exchange_rates:
            return amount * exchange_rates[currency_abbreviation]
        else:
            print(f"Warning: Currency {currency_abbreviation} not found, assuming COP")
            return amount

def get_wastes(fecha_inicial, fecha_final, convert_currency=True):
    session = Session()
    results = text("""
        SELECT 
            gasto_id, 
            cg.categoria, 
            description, 
            monto, 
            fecha,
            d.divisa,
            d.abreviacion,
            d.simbolo
        FROM 
            gastos g
        JOIN 
            categoria_gasto cg ON g.categoria = cg.categoria_id
        JOIN
            divisas d ON g.divisa = d.divisa_id
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

    data_list = []
    for result in results:
        original_amount = result[3]
        transaction_date = result[4]  # Fecha de la transacción
        currency_abbrev = result[6]
        
        # Convertir a COP si se solicita, usando la fecha de la transacción
        if convert_currency:
            amount_in_cop = convert_to_cop(original_amount, currency_abbrev, transaction_date)
            display_amount = amount_in_cop
            currency_display = "COP"
        else:
            display_amount = original_amount
            currency_display = currency_abbrev
        
        data_list.append({
            "Id": result[0],
            "Categoria": result[1],
            "Descripcion": result[2],
            "Monto": display_amount,
            "MontoOriginal": original_amount,
            "DivisaOriginal": currency_abbrev,
            "DivisaDisplay": currency_display,
            "Fecha": datetime.strftime(result[4], '%d/%m/%Y'),
            "Simbolo": result[7]
        })
        
    return jsonify(data_list)

def get_graph(fecha_inicial, fecha_final, convert_currency=True):
    session = Session()
    results = text("""
        SELECT
            cg.categoria,
            g.monto,
            d.abreviacion,
            g.fecha
        FROM
            gastos g
        JOIN
            categoria_gasto cg ON g.categoria = cg.categoria_id
        JOIN
            divisas d ON g.divisa = d.divisa_id
        WHERE
            g.fecha >= :fecha_inicial OR :fecha_inicial IS NULL
            AND g.fecha <= :fecha_final OR :fecha_final IS NULL;
    """)
    params = {'fecha_inicial': fecha_inicial,
                'fecha_final': fecha_final
              }
    
    results = session.execute(results, params).fetchall()    
    
    session.close()

    # Agrupar por categoría y sumar montos convertidos
    category_totals = {}
    for result in results:
        categoria = result[0]
        monto = result[1]
        currency_abbrev = result[2]
        transaction_date = result[3]
        
        # Convertir a COP si se solicita, usando la fecha de la transacción
        if convert_currency:
            monto_cop = convert_to_cop(monto, currency_abbrev, transaction_date)
        else:
            monto_cop = monto
        
        if categoria in category_totals:
            category_totals[categoria] += monto_cop
        else:
            category_totals[categoria] = monto_cop

    data_list = [{
        "Categoria": categoria,
        "Monto": monto,
        } for categoria, monto in category_totals.items()]
        
    return jsonify(data_list)