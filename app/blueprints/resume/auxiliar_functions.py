from sqlalchemy import (
    text
)
from . import resume
from app.extensions import Session
import app.blueprints.resume.consults as consults
from app.services.exchange_rate_service import ExchangeRateService
from datetime import date

def calculate_total_liquidity():
    """
    Calcula la liquidez total convirtiendo todos los saldos de cuentas a COP
    Returns: float - liquidez total en COP
    """
    try:
        # Obtener saldos detallados de todas las cuentas
        balances = consults.get_last_balance_by_account_detailed()
        
        if not balances:
            return 0.0
        
        # Obtener mapeo de divisas ID -> abreviación
        session = Session()
        try:
            divisa_query = text("""
                SELECT divisa_id, abreviacion
                FROM divisas;
            """)
            divisa_results = session.execute(divisa_query).fetchall()
            divisa_id_to_code = {item[0]: item[1] for item in divisa_results}
        finally:
            session.close()
        
        # Inicializar servicio de conversión
        exchange_service = ExchangeRateService()
        total_liquidity_cop = 0.0
        today = date.today()
        
        for balance in balances:
            saldo = balance['saldo']
            divisa_id = balance['divisa']
            
            # Obtener código de divisa
            divisa_code = divisa_id_to_code.get(divisa_id, 'COP')
            
            if divisa_code == 'COP':
                # Ya está en COP
                total_liquidity_cop += saldo
            else:
                # Convertir a COP usando la tasa actual
                try:
                    saldo_cop = exchange_service.convert_amount(saldo, divisa_code, 'COP', today)
                    total_liquidity_cop += saldo_cop
                except Exception as e:
                    print(f"Error convirtiendo {saldo} {divisa_code} a COP: {e}")
                    # En caso de error, usar tasa por defecto o saltar
                    continue
        
        return total_liquidity_cop
        
    except Exception as e:
        print(f"Error calculando liquidez total: {e}")
        return 0.0