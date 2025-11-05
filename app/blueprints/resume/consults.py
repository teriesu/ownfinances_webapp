from app.extensions import Session
from sqlalchemy import (
    text
)

def check_missing_elements(dictionary):
    session = Session()

    # Comprobar nuevas categorías de gastos
    missing_elements = {}
    cat_waste_values = tuple(dictionary['Categoría Gastos'])
    consult_categoria = text("""
        SELECT categoria
        FROM categoria_gasto
        WHERE categoria IN :values
    """)

    results_categoria = session.execute(consult_categoria, {'values': cat_waste_values}).fetchall()
    found_categories = [item[0] for item in results_categoria]
    
    missing_categories = [item for item in cat_waste_values if item not in found_categories]
    missing_categories = [item for item in missing_categories if item.strip()]

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
    missing_medios = [item for item in missing_medios if item.strip()]

    if missing_medios:
        missing_elements['Médio de pago'] = missing_medios

    
    # Comprobar Categoría Ingreso
    cat_income_values = tuple(dictionary['Categoría Ingreso'])
    consult_categoria_income = text("""
        SELECT categoria_ingreso
        FROM categoria_ingreso
        WHERE categoria_ingreso IN :values
    """)

    results_categoria_income = session.execute(consult_categoria_income, {'values': cat_income_values}).fetchall()
    found_categories_income = [item[0] for item in results_categoria_income]
    
    missing_categories_income = [item for item in cat_income_values if item not in found_categories_income]
    missing_categories_income = [item for item in missing_categories_income if item.strip()]
    if missing_categories_income:
        missing_elements['Categoría Ingreso'] = missing_categories_income
    

    #Comprobar Categoría Inversión
    cat_invest_values = tuple(dictionary['Categoría Inversión'])
    consult_categoria_invest = text("""
        SELECT categoria_inv
        FROM categoria_inversion
        WHERE categoria_inv IN :values
    """)
    results_categoria_invest = session.execute(consult_categoria_invest, {'values': cat_invest_values}).fetchall()
    found_categories_invest = [item[0] for item in results_categoria_invest]

    missing_categories_invest = [item for item in cat_invest_values if item not in found_categories_invest]
    missing_categories_invest = [item for item in missing_categories_invest if item.strip()]

    if missing_categories_invest:
        missing_elements['Categoría Inversión'] = missing_categories_invest
                                 
    #Comprobar plataforma inversión
    platf_invest_values = tuple(dictionary['Plataformas'])
    consult_categoria_invest = text("""
        SELECT plataforma
        FROM plataformas_inversion
        WHERE plataforma IN :values
    """)
    results_categoria_invest = session.execute(consult_categoria_invest, {'values': platf_invest_values}).fetchall()
    found_categories_invest = [item[0] for item in results_categoria_invest]

    missing_categories_invest = [item for item in platf_invest_values if item not in found_categories_invest]
    missing_categories_invest = [item for item in missing_categories_invest if item.strip()]
    
    if missing_categories_invest:
        missing_elements['Plataformas'] = missing_categories_invest

    session.close()

    return missing_elements

def get_last_format_register(hash_format, nombre_tabla):
    session = Session()

    consult_ultimo_registro = text(f"""
        SELECT max(id_df_formato)
        FROM {nombre_tabla}
        WHERE hash_formato = :hash_format;
    """)

    ultimo_registro = session.execute(consult_ultimo_registro, {'hash_format': hash_format}).fetchone()
    session.close()
    
    return ultimo_registro[0]   

def get_last_balance_by_account():
    """Devuelve {cuenta_id: saldo} con el último saldo por cuenta."""
    session = Session()
    try:
        consult_balance = text("""
            SELECT DISTINCT ON (cuenta_id)
                saldo_id,
                cuenta_id,
                saldo,
                fecha_movimiento,
                fecha_registro
            FROM public.saldo_cuenta
            ORDER BY cuenta_id, fecha_movimiento DESC, saldo_id DESC;
        """)
        
        rows = session.execute(consult_balance).mappings().all()
        # Construimos dict: cuenta_id -> saldo
        return {row['cuenta_id']: float(row['saldo']) for row in rows}
    finally:
        session.close()

def get_last_balance_by_account_detailed():
    """Devuelve {cuenta_id: saldo} con el último saldo por cuenta."""
    session = Session()
    try:
        consult_balance = text("""
            SELECT
            s.cuenta_id,
            s.saldo,
            c.divisa,
            ARRAY_AGG(mp.medio_pago_id) AS medios_pago
        FROM (
            SELECT DISTINCT ON (cuenta_id)
                cuenta_id,
                saldo,
                fecha_movimiento,
                saldo_id
            FROM public.saldo_cuenta
            ORDER BY cuenta_id, fecha_movimiento DESC, saldo_id DESC
        ) AS s
        JOIN cuentas c ON s.cuenta_id = c.cuenta_id
        LEFT JOIN medios_pago_cuentas mpc ON c.cuenta_id = mpc.cuenta_id
        LEFT JOIN medios_de_pago mp ON mpc.medio_pago_id = mp.medio_pago_id
        GROUP BY s.cuenta_id, s.saldo, c.divisa;
        """)
        
        rows = session.execute(consult_balance).fetchall()

        registro = [
            {
                'cuenta_id': row[0],
                'saldo': float(row[1]),
                'divisa': row[2],
                'medios_pago': row[3] if row[3] is not None else []
            }
            for row in rows
        ]

        print('registro', registro)

        return registro

    finally:
        session.close()
