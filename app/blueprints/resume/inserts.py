
from app.extensions import Session
from app.models import (
    CategoriaGasto,
    Medios_de_pago,
    Gastos,
    Bienes,
    Historical_money,
    Ingresos,
    Inversion,
    Categoria_ingreso,
    CategoriaInversion
)
from app.general_funcions import *
from sqlalchemy import (
    text
)
import datetime
import app.blueprints.resume.consults as consults
def actualize_db(dictionary):
    session = Session()
    
    missing_elements = consults.check_missing_elements(dictionary)
    
    if 'Categoría Gastos' in missing_elements:
        for categoria in missing_elements['Categoría Gastos']:
            new_categoria = CategoriaGasto(categoria)
            session.add(new_categoria)

    # Si hay medios de pago faltantes, insertarlos
    if 'Médio de pago' in missing_elements:
        for medio in missing_elements['Médio de pago']:
            new_medio = Medios_de_pago(medio)
            session.add(new_medio)
    
    if 'Categoría Ingreso' in missing_elements:
        for categoria in missing_elements['Categoría Ingreso']:
            new_categoria = Categoria_ingreso(categoria)
            session.add(new_categoria)

    if 'Categoría Inversión' in missing_elements:
        for categoria in missing_elements['Categoría Inversión']:
            new_categoria = CategoriaInversion(categoria)
            session.add(new_categoria)
    
    session.commit()
    session.close()

def update_current_money(patrimonio, liquidez, description):

    session = Session()

    fecha_actual = datetime.datetime.now()
    nuevo_registro = Historical_money(
        fecha=fecha_actual,
        patrimonio=patrimonio,
        liquidez=liquidez,
        description = description
    )
    session.add(nuevo_registro)
    session.commit()

def save_incomings(df, file_id, sheet_name):
    session = Session()
    try:
        df['Monto'] = df['Monto'].apply(convert_currency_to_int)
        df['Categoría'] = df['Categoría'].map(cat_incom_string_to_id())
        _, patrimonio, liquidez = get_current_heritage()
        last_incoming_id = consults.get_last_format_register(file_id, hoja_tabla[sheet_name])
        start_index = last_incoming_id + 1 if last_incoming_id is not None else 0
        iterated = False
        for index, row in df.iloc[start_index:].iterrows():
            iterated = True
            nuevo_ingreso = Ingresos(
                description = row['Descripción'],
                monto = row['Monto'],
                fecha = row['Fecha'],
                categoria = row['Categoría'],
                hash_formato = file_id,
                id_df_formato = index, 
            )
            session.add(nuevo_ingreso)
            liquidez += row['Monto']
        
        if iterated:
            update_current_money(patrimonio, liquidez, row['Descripción'])
        
        session.commit()
        return "Datos guardados con éxito.", 'success'
    
    except Exception as e:
        session.rollback()
        return f"Error al guardar los datos: {e}", 'danger'

    finally:
        session.close()

def save_wastes(df, file_id, sheet_name):
    session = Session()
    try:
        df['Monto'] = df['Monto'].apply(convert_currency_to_int)
        df['Categoría'] = df['Categoría'].map(cat_wast_string_to_id)
        df['Médio de pago'] = df['Médio de pago'].map(medio_string_to_id)

        _, patrimonio, liquidez = get_current_heritage()
        
        last_waste_id = consults.get_last_format_register(file_id, hoja_tabla[sheet_name])
        start_index = last_waste_id + 1 if last_waste_id is not None else 0
        iterated = False
        for index, row in df.iloc[start_index:].iterrows():
            iterated = True
            nuevo_bien = None
            if row['Categoría'] == 10:
                nuevo_bien = Bienes(
                    description=row['Bien'],
                    valor_inicial=row['Monto']
                )
                session.add(nuevo_bien)
                session.commit()
                patrimonio += row['Monto']
            
            nuevo_gasto = Gastos(
                description=row['Descripción'],
                monto=row['Monto'],
                fecha=row['Fecha'],
                categoria=row['Categoría'],
                hash_formato=file_id,
                id_df_formato=index,
                id_patrimonio=nuevo_bien.bien_id if nuevo_bien is not None else None,
                essential = True if row['Fecha'] == 'Si' else False
            )
            session.add(nuevo_gasto)
            liquidez -= row['Monto']
        
        if iterated:
            update_current_money(patrimonio, liquidez, row['Descripción'])

        session.commit()
        return "Datos guardados con éxito.", 'success'

    except Exception as e:
        session.rollback()
        return f"Error al guardar los datos: {e}", 'danger'

    finally:
        session.close()

def save_investments(df, file_id, sheet_name):
    session = Session()
    df['Monto'] = df['Monto'].apply(convert_currency_to_int)
    df['Categoría'] = df['Categoría'].map(cat_invest_string_to_id())
    _, patrimonio, liquidez = get_current_heritage()
    last_investment_id = consults.get_last_format_register(file_id, hoja_tabla[sheet_name])
    start_index = last_investment_id + 1 if last_investment_id is not None else 0
    iterated = False
    for index, row in df.iloc[start_index:].iterrows():
        iterated = True
        nuevo_inversion = Inversion(
            description = row['Descripción'],
            monto = row['Monto'],
            fecha = row['Fecha'],
            categoria = row['Categoría'],
            hash_formato = file_id,
            id_df_formato = index, 
        )
        session.add(nuevo_inversion)
        liquidez -= row['Monto']