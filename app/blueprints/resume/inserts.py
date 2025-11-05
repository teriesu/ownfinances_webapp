
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

def update_current_money(suma_por_medio_divisa, total_records_expected):
    """
    Actualiza saldos de cuentas solo si todos los registros fueron procesados correctamente
    Args:
        suma_por_medio_divisa: Diccionario con sumas agrupadas por medio y divisa
        total_records_expected: Número total de registros que deberían haberse procesado
    Returns:
        tuple: (success: bool, message: str)
    """
    session = Session()
    try:
        # Verificar que se procesaron todos los registros esperados
        total_processed = sum(1 for key in suma_por_medio_divisa if suma_por_medio_divisa[key]['total'] > 0)
        if total_processed != total_records_expected:
            return False, f"Error: Se esperaban {total_records_expected} registros, pero solo se procesaron {total_processed} correctamente."
        
        # Obtener nombres de medios de pago y divisas para mensajes más legibles
        medios_dict = medio_id_to_string()  # {id: nombre}
        divisas_dict = divisa_id_to_string()  # {id: nombre}
        
        last_balance = consults.get_last_balance_by_account_detailed()
        nuevos_saldos = []
        
        # Verificar que cada combinación medio-divisa tenga una cuenta correspondiente
        unmatched_combinations = []
        
        for medio_id, divisa_id in suma_por_medio_divisa:
            found_match = False
            
            # Obtener nombres legibles
            medio_nombre = medios_dict.get(medio_id, f"ID:{medio_id}")
            divisa_nombre = divisas_dict.get(divisa_id, f"ID:{divisa_id}")
            
            for balance_account in last_balance: 
                if medio_id in balance_account['medios_pago'] and divisa_id == balance_account['divisa']:
                    found_match = True
                    nuevo_saldo = SaldoCuenta(
                        cuenta_id=balance_account['cuenta_id'],
                        saldo=balance_account['saldo'] - suma_por_medio_divisa[(medio_id, divisa_id)]['total'],
                        fecha_movimiento=suma_por_medio_divisa[(medio_id, divisa_id)]['last_fecha'],
                        descripcion=suma_por_medio_divisa[(medio_id, divisa_id)]['last_desc']
                    )
                    nuevos_saldos.append(nuevo_saldo)
                    break
            
            if not found_match:
                unmatched_combinations.append(f"Medio: {medio_nombre} (ID:{medio_id}), Divisa: {divisa_nombre} (ID:{divisa_id})")
        
        # Si hay combinaciones sin cuenta correspondiente, no proceder
        if unmatched_combinations:
            error_msg = f"Error: No se encontraron cuentas para las siguientes combinaciones:\n" + "\n".join(unmatched_combinations)
            return False, error_msg
        
        # Si llegamos aquí, todo está bien para proceder
        session.add_all(nuevos_saldos)
        session.commit()
        return True, f"Se actualizaron {len(nuevos_saldos)} saldos de cuenta correctamente."
        
    except Exception as e:
        session.rollback()
        return False, f"Error al actualizar saldos: {e}"
    finally:
        session.close()
    

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
        
        # Procesar datos
        df = df.copy()
        df['Monto'] = df['Monto'].apply(convert_currency_to_float)
        df['Categoría'] = df['Categoría'].map(cat_wast_string_to_id())
        df['Médio de pago'] = df['Médio de pago'].map(medio_string_to_id())
        df['Divisa'] = df['Divisa'].map(divisa_string_to_id())
        
        last_waste_id = consults.get_last_format_register(file_id, hoja_tabla[sheet_name])
        start_index = last_waste_id + 1 if last_waste_id is not None else 0
        
        # Filtrar registros a procesar
        records_to_process = df.iloc[start_index:]
        if records_to_process.empty:
            return "No hay registros nuevos para procesar.", 'info'
        
        # FASE 1: VALIDACIÓN PREVIA - Verificar que todos los registros se pueden procesar
        validation_errors = []
        
        # Guardar los valores originales para mensajes más descriptivos
        df_original = df.copy()
        
        for index, row in records_to_process.iterrows():
            # Obtener valores originales antes del mapeo
            original_categoria = df_original.loc[index, 'Categoría'] if index in df_original.index else 'N/A'
            original_medio = df_original.loc[index, 'Médio de pago'] if index in df_original.index else 'N/A'
            original_divisa = df_original.loc[index, 'Divisa'] if index in df_original.index else 'N/A'
            
            # Verificar que los mapeos fueron exitosos (no son None)
            if pd.isna(row['Categoría']) or row['Categoría'] is None:
                validation_errors.append(f"Fila {index}: Categoría no válida '{original_categoria}'")
            
            if pd.isna(row['Médio de pago']) or row['Médio de pago'] is None:
                validation_errors.append(f"Fila {index}: Medio de pago no válido '{original_medio}'")
            
            if pd.isna(row['Divisa']) or row['Divisa'] is None:
                validation_errors.append(f"Fila {index}: Divisa no válida '{original_divisa}'")
            
            if pd.isna(row['Monto']) or row['Monto'] is None or row['Monto'] <= 0:
                validation_errors.append(f"Fila {index}: Monto no válido '{row['Monto']}'")
        
        # Si hay errores de validación, abortar antes de cualquier commit
        if validation_errors:
            error_msg = "Errores de validación encontrados:\n" + "\n".join(validation_errors[:10])  # Mostrar solo los primeros 10
            if len(validation_errors) > 10:
                error_msg += f"\n... y {len(validation_errors) - 10} errores más."
            return error_msg, 'danger'
        
        # FASE 2: PROCESAMIENTO - Ahora que sabemos que todos los datos son válidos
        suma_por_medio_divisa = defaultdict(lambda: {'total': 0.0, 'last_desc': None, 'last_fecha': None})
        nuevos_gastos = []
        nuevos_bienes = []
        records_processed = 0
        
        for index, row in records_to_process.iterrows():
            # Procesar bienes si es categoría 10
            nuevo_bien = None
            if row['Categoría'] == 10 and 'Bien' in row and not pd.isna(row['Bien']):
                nuevo_bien = Bienes(
                    description=row['Bien'],
                    valor_inicial=row['Monto']
                )
                nuevos_bienes.append(nuevo_bien)
            
            # Crear registro de gasto
            nuevo_gasto = Gastos(
                description=row['Descripción'],
                monto=row['Monto'],
                fecha=row['Fecha'],
                categoria=row['Categoría'],
                hash_formato=file_id,
                id_df_formato=index,
                id_patrimonio=None,  # Se asignará después si hay bien
                essential=True if row.get('Esencial', '') == 'Si' else False,
                divisa=row['Divisa'],
                medio_pago_id=row['Médio de pago']
            )
            nuevos_gastos.append(nuevo_gasto)
            
            # Acumular por medio y divisa
            medio_id = row['Médio de pago']
            divisa_id = row['Divisa']
            monto = float(row['Monto'])
            fecha = row['Fecha']
            
            key = (medio_id, divisa_id)
            agg = suma_por_medio_divisa[key]
            agg['total'] += monto
            agg['last_desc'] = row['Descripción']
            agg['last_fecha'] = fecha
            
            records_processed += 1
        
        # FASE 3: VALIDAR ACTUALIZACIÓN DE SALDOS
        balance_update_success, balance_message = update_current_money(suma_por_medio_divisa, records_processed)
        
        if not balance_update_success:
            # Si no se pueden actualizar los saldos, abortar todo
            return f"Error en actualización de saldos: {balance_message}", 'danger'
        
        # FASE 4: COMMIT FINAL - Solo si todo está correcto
        # Primero guardar bienes (para obtener IDs)
        if nuevos_bienes:
            session.add_all(nuevos_bienes)
            session.flush()  # Obtener IDs sin commit final
            
            # Asignar IDs de bienes a gastos correspondientes
            bien_index = 0
            for gasto in nuevos_gastos:
                if gasto.categoria == 10:
                    gasto.id_patrimonio = nuevos_bienes[bien_index].bien_id
                    bien_index += 1
        
        # Guardar gastos
        session.add_all(nuevos_gastos)
        
        # Commit final
        session.commit()
        
        success_msg = f"Operación exitosa:\n"
        success_msg += f" {len(nuevos_gastos)} gastos guardados\n"
        if nuevos_bienes:
            success_msg += f"- {len(nuevos_bienes)} bienes registrados\n"
        success_msg += f"- {balance_message}"
        
        return success_msg, 'success'

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
