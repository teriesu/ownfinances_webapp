
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
    CategoriaInversion,
    PlataformasInversion,
    SaldoCuenta
)
from app.general_funcions import *
from sqlalchemy import (
    text
)
from collections import defaultdict
import datetime
import app.blueprints.resume.consults as consults
import pandas as pd

def validate_essential_columns(df, required_columns, data_type="datos"):
    """
    Valida que las columnas esenciales no tengan valores vacíos
    Args:
        df: DataFrame a validar
        required_columns: Lista de columnas que son obligatorias
        data_type: Tipo de datos para el mensaje de error
    Returns:
        tuple: (is_valid, error_message)
    """
    missing_data = []
    
    for col in required_columns:
        if col not in df.columns:
            missing_data.append(f"Columna '{col}' no encontrada")
            continue
            
        # Verificar valores nulos o vacíos
        null_mask = df[col].isnull()
        empty_mask = df[col].astype(str).str.strip() == ''
        invalid_rows = df[null_mask | empty_mask]
        
        if not invalid_rows.empty:
            invalid_indices = invalid_rows.index.tolist()
            missing_data.append(f"Columna '{col}': filas {invalid_indices} tienen valores vacíos")
    
    if missing_data:
        error_msg = f"Error de validación en {data_type}:\n" + "\n".join(missing_data)
        return False, error_msg
    
    return True, None

def actualize_db(dictionary):
    session = Session()
    
    missing_elements = consults.check_missing_elements(dictionary)
    
    if 'Categoría Gastos' in missing_elements:
        for categoria in missing_elements['Categoría Gastos']:
            new_categoria = CategoriaGasto(categoria)
            session.add(new_categoria)

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

    if 'Plataformas' in missing_elements:
        for plataforma in missing_elements['Plataformas']:
            new_plataforma = PlataformasInversion(plataforma)
            session.add(new_plataforma)
    
    session.commit()
    session.close()

def update_current_money(suma_por_medio_divisa):
    last_balance = consults.get_last_balance_by_account_detailed()
    # print("Last balance:", last_balance)
    # (medio_id, divisa_id)
    # print("Suma por medio y divisa:", suma_por_medio_divisa)
    

def save_incomings(df, file_id, sheet_name):
    session = Session()
    try:
        if df.empty:
            return "No hay ingresos nuevos.", 'info'

        required_columns = ['Descripción', 'Monto', 'Fecha', 'Categoría', 'Cuenta']
        is_valid, error_msg = validate_essential_columns(df, required_columns, "ingresos")
        if not is_valid:
            return error_msg, 'danger'

        last_incoming_id = consults.get_last_format_register(file_id, 'saldo_cuenta')
        start_index = last_incoming_id + 1 if last_incoming_id is not None else 0

        # Limpieza / normalización
        df = df.copy()
        df['Monto'] = df['Monto'].apply(convert_currency_to_float).astype(float)
        df['Categoría'] = df['Categoría'].map(cat_incom_string_to_id())
        df['Cuenta'] = df['Cuenta'].map(cuenta_string_to_id())

        # Ordena para que el saldo vaya “acumulando” por cuenta
        df.sort_values(['Cuenta', 'Fecha'], inplace=True)

        # Trae últimos saldos actuales y prepáralos para ir actualizando
        last_balance_by_account = consults.get_last_balance_by_account()
        running_balances = defaultdict(float, last_balance_by_account)

        nuevos = []
        for index, row in df.iloc[start_index:].iterrows():
            cuenta_id = int(row['Cuenta'])
            monto = float(row['Monto'])
            fecha = row['Fecha']

            # saldo acumulado por cuenta
            new_balance = running_balances[cuenta_id] + monto

            nuevo_ingreso = SaldoCuenta(
                cuenta_id=cuenta_id,
                fecha_movimiento=fecha,
                saldo=new_balance,
                descripcion=row['Descripción'],
                hash_formato=file_id,
                id_df_formato=index
            )
            nuevos.append(nuevo_ingreso)

            # Actualiza el acumulado en RAM para la siguiente fila de la misma cuenta
            running_balances[cuenta_id] = new_balance

        if not nuevos:
            return "No hay ingresos nuevos válidos para guardar.", 'info'

        session.add_all(nuevos)
        session.commit()
        return f"Se guardaron {len(nuevos)} ingresos.", 'success'
    
    except Exception as e:
        session.rollback()
        return f"Error al guardar los ingresos: {e}", 'danger'

    finally:
        session.close()

def save_wastes(df, file_id, sheet_name):
    session = Session()
    try:
        if df.empty:
            return "No hay gastos nuevos.", 'info'
        
        # Validar columnas esenciales para gastos
        required_columns = ['Descripción', 'Monto', 'Fecha', 'Categoría', 'Médio de pago', 'Divisa']
        is_valid, error_msg = validate_essential_columns(df, required_columns, "gastos")
        if not is_valid:
            return error_msg, 'danger'
        
        df['Monto'] = df['Monto'].apply(convert_currency_to_float)
        df['Categoría'] = df['Categoría'].map(cat_wast_string_to_id())
        df['Médio de pago'] = df['Médio de pago'].map(medio_string_to_id())
        df['Divisa']  = df['Divisa'].map(divisa_string_to_id())
        
        last_waste_id = consults.get_last_format_register(file_id, hoja_tabla[sheet_name])
        start_index = last_waste_id + 1 if last_waste_id is not None else 0
        iterated = False
        suma_por_medio_divisa = defaultdict(lambda: {'total': 0.0, 'last_desc': None, 'last_fecha': None})
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
            #     patrimonio += row['Monto']

            medio_id = row['Médio de pago']
            divisa_id = row['Divisa']
            monto = float(row['Monto']) if row['Monto'] is not None else 0.0
            fecha = row['Fecha']

            nuevo_gasto = Gastos(
                description=row['Descripción'],
                monto=row['Monto'],
                fecha=row['Fecha'],
                categoria=row['Categoría'],
                hash_formato=file_id,
                id_df_formato=index,
                id_patrimonio=nuevo_bien.bien_id if nuevo_bien is not None else None,
                essential = True if row['Fecha'] == 'Si' else False,
                divisa = row['Divisa'],
                medio_pago_id = row['Médio de pago']
            )
            session.add(nuevo_gasto)
        
            if medio_id is not None and divisa_id is not None:
                key = (medio_id, divisa_id)
                agg = suma_por_medio_divisa[key]
                agg['total'] += monto
                agg['last_desc'] = row['Descripción']
                agg['last_fecha'] = fecha

        if iterated:
            update_current_money(suma_por_medio_divisa)

        # session.commit()
        return "Gastos guardados con éxito.", 'success'

    except Exception as e:
        session.rollback()
        return f"Error al guardar los gastos: {e}", 'danger'

    finally:
        session.close()

def save_investments(df, file_id, sheet_name):
    session = Session()
    
    try:
        if df.empty:
            return "No hay inversiones nuevas.", 'info'
        
        # Validar columnas esenciales para inversiones
        required_columns = ['Descripción', 'Monto', 'Rentabilidad Esperada', 'Fecha', 'Categoría']
        is_valid, error_msg = validate_essential_columns(df, required_columns, "inversiones")
        if not is_valid:
            return error_msg, 'danger'
        
        df['Monto'] = df['Monto'].apply(convert_currency_to_float)
        df['Categoría'] = df['Categoría'].map(cat_invest_string_to_id())

        last_investment_id = consults.get_last_format_register(file_id, hoja_tabla[sheet_name])
        start_index = last_investment_id + 1 if last_investment_id is not None else 0

        iterated = False
        for index, row in df.iloc[start_index:].iterrows():
            iterated = True
            nuevo_inversion = Inversion(
                description = row['Descripción'], 
                monto = row['Monto'], 
                rentab_esperada = row['Rentabilidad Esperada'], 
                fecha = row['Fecha'], 
                categoria = row['Categoría'], 
                hash_formato = file_id, 
                id_df_formato = index
            )
            session.add(nuevo_inversion)
            patrimonio += row['Monto']
            liquidez -= row['Monto']

        # if iterated:
        #     update_current_money(patrimonio, liquidez, row['Descripción'])
        
        # session.commit()
        return "Inversiones guardadas con éxito.", 'success'

    except Exception as e:
        session.rollback()
        return f"Error al guardar las inversiones: {e}", 'danger'

    finally:
        session.close()
