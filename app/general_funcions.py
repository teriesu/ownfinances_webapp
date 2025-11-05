from app.extensions import Session
from sqlalchemy import text

hoja_tabla = {
    'Compras-Gastos': 'gastos',
    'Inversiones': 'inversion',
    'Ingresos': 'ingresos'
}

def convert_currency_to_float(currency_str):
    # Eliminar el símbolo de dólar y los puntos, y luego convertir a float
    without_thousands = currency_str.replace('$', '').replace('.', '')
    return float(without_thousands.replace(',', '.'))

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

def divisa_string_to_id():
    session = Session()

    consult_divisa = text("""
        SELECT divisa_id, abreviacion
        FROM divisas;
    """)
    results_divisa = session.execute(consult_divisa).fetchall()

    divisa_dict = {item[1]: item[0] for item in results_divisa}
    
    return divisa_dict

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

def cuenta_string_to_id():
    session = Session()

    consult_cuenta = text("""
        SELECT cuenta_id, nombre_cuenta
        FROM cuentas;
    """)
    results_cuenta = session.execute(consult_cuenta).fetchall()

    cuenta_dict = {item[1]: item[0] for item in results_cuenta}
    
    return cuenta_dict