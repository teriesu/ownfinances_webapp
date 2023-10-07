
from app.extensions import Session
from app.models import (
    CategoriaGasto,
    Medios_de_pago
)
from sqlalchemy import (
    text
)
import app.blueprints.resume.consults as consults
def actualize_db(dictionary):
    session = Session()
    
    missing_elements = consults.check_missing_elements(dictionary)
    
    if 'Categoría Gastos' in missing_elements:
        for categoria in missing_elements['Categoría Gastos']:
            new_categoria = CategoriaGasto(categoria)
            session.add(new_categoria)

    # Si hay medios de pago faltantes, insertarlos
    if 'Medio de pago' in missing_elements:
        for medio in missing_elements['Medio de pago']:
            new_medio = Medios_de_pago(medio)
            session.add(new_medio)
    
    session.commit()
    session.close()

def save_wastes(df):

    print(df)
