"""
Servicio para manejo de tasas de cambio dinámicas
Usa APIs externas con cache en memoria, sin dependencia de base de datos
"""

import requests
from datetime import datetime, date, timedelta
from typing import Dict, Optional
import json

class ExchangeRateService:
    
    def __init__(self):
        # Cache en memoria para tasas (se limpia al reiniciar la app)
        self._cache: Dict[str, Dict[str, float]] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        
        # Configuración de APIs
        self.apis = {
            'banco_republica': {
                'url': 'https://www.banrep.gov.co/sites/default/files/webservices/dolar/data.json',
                'timeout': 10
            },
            'exchangerate_api': {
                'url': 'https://api.exchangerate-api.com/v4/latest/USD',
                'timeout': 10
            }
        }
        
        # Tasas por defecto como último recurso
        self.default_rates = {
            'USD': 4200.0,
            'EUR': 4600.0,
            'GBP': 5300.0,
            'JPY': 28.0,
            'CAD': 3100.0,
            'BRL': 850.0,
            'MXN': 245.0,
            'COP': 1.0
        }
    
    def _get_cache_key(self, from_currency: str, to_currency: str, target_date: date) -> str:
        """Genera clave única para el cache"""
        return f"{from_currency}_{to_currency}_{target_date.isoformat()}"
    
    def _is_cache_valid(self, cache_key: str, max_age_hours: int = 24) -> bool:
        """Verifica si el cache sigue siendo válido"""
        if cache_key not in self._cache_expiry:
            return False
        
        expiry_time = self._cache_expiry[cache_key]
        return datetime.now() < expiry_time + timedelta(hours=max_age_hours)
    
    def _set_cache(self, cache_key: str, rate: float):
        """Guarda tasa en cache"""
        if 'rates' not in self._cache:
            self._cache['rates'] = {}
        
        self._cache['rates'][cache_key] = rate
        self._cache_expiry[cache_key] = datetime.now()
    
    def _get_cache(self, cache_key: str) -> Optional[float]:
        """Obtiene tasa del cache si es válida"""
        if self._is_cache_valid(cache_key):
            return self._cache.get('rates', {}).get(cache_key)
        return None
    
    def get_cop_rate_from_banrep(self, target_date: Optional[date] = None) -> Optional[float]:
        """
        Obtiene la TRM del Banco de la República de Colombia
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            # Para fechas muy antiguas, usar tasa por defecto
            if target_date < date.today() - timedelta(days=730):
                return self.default_rates.get('USD')
            
            response = requests.get(
                self.apis['banco_republica']['url'], 
                timeout=self.apis['banco_republica']['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                target_str = target_date.strftime('%Y-%m-%d')
                
                # Buscar la tasa para la fecha específica
                for record in data:
                    if record.get('vigenciadesde') == target_str:
                        return float(record.get('valor', 0))
                
                # Si no se encuentra, usar la más reciente
                if data and isinstance(data, list) and len(data) > 0:
                    most_recent = data[0]
                    if 'valor' in most_recent:
                        return float(most_recent['valor'])
                        
        except Exception as e:
            print(f"Error getting TRM from Banco República: {e}")
            return None
    
    def get_rate_from_exchangerate_api(self, from_currency: str, target_date: Optional[date] = None) -> Optional[float]:
        """
        Obtiene tasas de cambio desde ExchangeRate-API
        """
        try:
            if target_date is None:
                target_date = date.today()
            
            # Para fechas muy antiguas, usar tasa por defecto
            if target_date < date.today() - timedelta(days=730):
                return self.default_rates.get(from_currency)
            
            response = requests.get(
                self.apis['exchangerate_api']['url'],
                timeout=self.apis['exchangerate_api']['timeout']
            )
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                
                # Obtener tasa USD -> COP del Banco República
                usd_to_cop = self.get_cop_rate_from_banrep(target_date)
                if not usd_to_cop:
                    usd_to_cop = self.default_rates['USD']
                
                if from_currency == 'USD':
                    return usd_to_cop
                elif from_currency in rates:
                    # Convertir: FROM -> USD -> COP
                    usd_rate = 1 / rates[from_currency]  # FROM -> USD
                    return usd_rate * usd_to_cop  # FROM -> COP
                    
        except Exception as e:
            print(f"Error getting rate from ExchangeRate API: {e}")
            return None
    
    def get_exchange_rate(self, from_currency: str, to_currency: str, target_date: Optional[date] = None) -> float:
        """
        Obtiene tasa de cambio con estrategia de fallback
        """
        if target_date is None:
            target_date = date.today()
        
        # Caso especial: misma divisa
        if from_currency == to_currency:
            return 1.0
        
        # Solo soportamos conversión a COP por ahora
        if to_currency != 'COP':
            return 1.0
        
        # 1. Verificar cache
        cache_key = self._get_cache_key(from_currency, to_currency, target_date)
        cached_rate = self._get_cache(cache_key)
        if cached_rate:
            return cached_rate
        
        # 2. Intentar APIs para fechas recientes
        rate = None
        if target_date >= date.today() - timedelta(days=7):
            if from_currency == 'USD':
                rate = self.get_cop_rate_from_banrep(target_date)
            else:
                rate = self.get_rate_from_exchangerate_api(from_currency, target_date)
        
        # 3. Si no se obtuvo de API, usar tasa por defecto
        if not rate:
            rate = self.default_rates.get(from_currency, 1.0)
        
        # Guardar en cache
        if rate:
            self._set_cache(cache_key, rate)
        
        return rate
    
    def convert_amount(self, amount: float, from_currency: str, to_currency: str, transaction_date) -> float:
        """
        Convierte un monto usando la tasa del día de la transacción
        """
        if isinstance(transaction_date, str):
            transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
        elif isinstance(transaction_date, datetime):
            transaction_date = transaction_date.date()
        
        rate = self.get_exchange_rate(from_currency, to_currency, transaction_date)
        return amount * rate