from app.extensions import Session
from sqlalchemy import text

hoja_tabla = {
    'Compras-Gastos': 'gastos',
    'Inversiones': 'inversion',
    'Ingresos': 'ingresos'
}

def convert_currency_to_int(currency_str):
    # Eliminar el símbolo de dólar y los puntos, y luego convertir a entero
    return int(currency_str.replace('$', '').replace('.', ''))

def cat_wast_string_to_id():
    session = Session()

    consult_categoria = text("""
        SELECT categoria_id, categoria
        FROM categoria_gasto;
    """)
    results_categoria = session.execute(consult_categoria).fetchall()

    categoria_dict = {item[1]: item[0] for item in results_categoria}
    
    return categoria_dict

def medio_string_to_id():
    session = Session()

    consult_medio = text("""
        SELECT medio_pago_id, medio_pago
        FROM medios_de_pago;
    """)
    results_medio = session.execute(consult_medio).fetchall()

    medio_dict = {item[1]: item[0] for item in results_medio}
    
    return medio_dict

def get_current_heritage():

    session = Session()

    consult_patrimonio = text("""
        SELECT fecha, patrimonio, liquidez
	        FROM public.historical_money
            ORDER BY fecha DESC
            LIMIT 1;
    """)

    results_patrimonio = session.execute(consult_patrimonio).fetchone()
    session.close()

    return results_patrimonio

def cat_incom_string_to_id():
    session = Session()

    consult_categoria = text("""
        SELECT categoria_ingreso_id, categoria_ingreso
        FROM categoria_ingreso;
    """)
    results_categoria = session.execute(consult_categoria).fetchall()

    categoria_dict = {item[1]: item[0] for item in results_categoria}
    
    return categoria_dict

def cat_invest_string_to_id():
    session = Session()

    consult_categoria = text("""
        SELECT categoria_inv_id, categoria_inv
        FROM categoria_inversion;
    """)
    results_categoria = session.execute(consult_categoria).fetchall()

    categoria_dict = {item[1]: item[0] for item in results_categoria}
    
    return categoria_dict