from app.extensions import Session
from sqlalchemy import (
    text
)

def check_missing_elements(dictionary):
    session = Session()

    missing_elements = {}
    cat_values = tuple(dictionary['Categoría Gastos'])
    consult_categoria = text("""
        SELECT categoria
        FROM categoria_gasto
        WHERE categoria IN :values
    """)

    results_categoria = session.execute(consult_categoria, {'values': cat_values}).fetchall()
    found_categories = [item[0] for item in results_categoria]
    
    missing_categories = [item for item in cat_values if item not in found_categories]
    if missing_categories:
        missing_elements['Categoría Gastos'] = missing_categories

    # Comprobar Medios de Pago
    medio_values = tuple(dictionary['Medio de pago'])
    consult_medio = text("""
        SELECT medio_pago
        FROM medios_de_pago
        WHERE medio_pago IN :values
    """)
    results_medio = session.execute(consult_medio, {'values': medio_values}).fetchall()
    found_medios = [item[0] for item in results_medio]
    
    missing_medios = [item for item in medio_values if item not in found_medios]
    if missing_medios:
        missing_elements['Medio de pago'] = missing_medios

    session.close()

    return missing_elements