import gspread
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import pandas as pd

class Gdrive:
    def _auth(self):
            # Reemplaza 'your_credentials_file.json' con el nombre del archivo JSON descargado en el paso 2
            creds = None
            creds_file = 'gkey.json'

            if os.path.exists(creds_file):
                creds = service_account.Credentials.from_service_account_file(creds_file, scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

            if not creds:
                raise Exception('No se pudo obtener las credenciales de Google API')

            # Inicializa el cliente de Google Drive API
            drive_service = build('drive', 'v3', credentials=creds)
            sheets_service = build('sheets', 'v4', credentials=creds)

            return drive_service, sheets_service
    
    def get_folder_id(self, folder_name):
        drive_service, _ = self._auth()
        query = "mimeType='application/vnd.google-apps.folder' and name='{}'".format(folder_name)
        results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        folders = results.get("files", [])

        if not folders:
            raise Exception('No se encontró la carpeta en Google Drive')

        folder_id = folders[0]['id']
        return folder_id
    
    def get_file_id(self, file_name):
        drive_service, _ = self._auth()
        
        # Busca archivos que coincidan con el nombre proporcionado
        query = "name='{}'".format(file_name)
        results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        
        # Obtiene la lista de archivos que coinciden
        files = results.get("files", [])

        # Si no hay coincidencias, levanta una excepción
        if not files:
            raise Exception('No se encontró el archivo en Google Drive')

        # Retorna el ID del primer archivo que coincida (suponiendo que hay un único archivo con ese nombre)
        file_id = files[0]['id']
        return file_id

    def get_files(self, folder_name):

        drive_service, _ = self._auth()
        query = "mimeType='application/vnd.google-apps.folder' and name='{}'".format(folder_name)
        results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        folders = results.get("files", [])

        if not folders:
            raise Exception('No se encontró la carpeta en Google Drive')

        folder_id = folders[0]['id']
        query = "'{}' in parents".format(folder_id)
        results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        files = results.get("files", [])
        file_list = []
        if not files:
            print('No se encontraron archivos en la carpeta')
            return None
        else:
            for file in files:
                file_list.append([file['name'], file['id']])
        return file_list
    
    def copy_file(self, source_file_id, detination_folder, destination_file_name):
        drive_service, _ = self._auth()
        
        destination_folder_id = self.get_folder_id(detination_folder)

        # Realiza una copia del archivo de Google Sheets en Google Drive
        copied_file = {
            'name': destination_file_name,
            'parents': [destination_folder_id]
        }
        file = drive_service.files().copy(fileId=source_file_id, body=copied_file).execute()
        print(f'Archivo copiado con ID: "{file.get("id")}" y nombre "{file.get("name")}" en la carpeta con ID "{destination_folder_id}".')

    def delete_file(self, file_id):
        drive_service, _ = self._auth()
        drive_service.files().delete(fileId=file_id).execute()
        print(f'Archivo con ID "{file_id}" eliminado.')
    
    def write_sheet_cols(self, file_name, sheet_name, data_dict):
        _, sheets_service = self._auth()
        file_id = self.get_file_id(file_name)
        # Establece el rango de inicio. En este caso, se comienza desde la columna A
        column_index = 0
        for key, values in data_dict.items():
            # Agrega la clave del diccionario como la primera fila
            column_data = [key] + values
            
            range_name = f'{sheet_name}!{chr(65 + column_index)}1:{chr(65 + column_index)}{len(column_data)}' # Esto convierte 0 -> A, 1 -> B, etc. y añade el nombre de la hoja
            
            # Usa la API de Google Sheets para escribir los datos en la hoja de cálculo
            request = sheets_service.spreadsheets().values().update(
                spreadsheetId=file_id,
                range=range_name,
                valueInputOption="RAW",
                body={
                    "values": [[value] for value in column_data]
                }
            )
            response = request.execute()
            
            # Incrementa el índice de la columna para moverse a la siguiente columna
            column_index += 1

        return response
    
    def read_sheet_as_dataframe(self, file_name, sheet_name):
        _, sheets_service = self._auth()
        file_id = self.get_file_id(file_name)
        # Usa la API de Google Sheets para obtener los valores de la hoja específica
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=file_id,
            range=sheet_name
        ).execute()
        
        # Obtiene los valores desde el resultado
        values = result.get('values', [])
        
        if not values:
            return pd.DataFrame()  # Retorna un DataFrame vacío si no hay datos
        
        # Asegúrate de que todas las filas tengan la misma longitud
        num_columns = len(values[0])
        for row in values[1:]:
            while len(row) < num_columns:
                row.append('')  # Agrega valores vacíos para filas cortas

        # Convierte los valores en un DataFrame de pandas
        df = pd.DataFrame(values[1:], columns=values[0])
        
        return df

    
    def get_columns_as_dict(self, file_name, sheet_name):
        df = self.read_sheet_as_dataframe(file_name, sheet_name)
        
        # Convertir el DataFrame en un diccionario
        column_dict = df.to_dict(orient='list')

        # Limpia las listas para remover valores NaN
        for key, value in column_dict.items():
            column_dict[key] = [v for v in value if pd.notna(v)]

        return column_dict

if __name__ == '__main__':
    gdrive = Gdrive()
    # print(gdrive.get_files('Formatos')[0][1])

    #COPIAR FORMATO
    # gdrive.copy_file(gdrive.get_files('Formatos')[0][1], 'Own finances', 'Registrar información')

    # data_dict = {
    #     'Gastos': ['Compras', 'Alimentos', 'Transporte', 'Servicios', 'Entretenimiento', 'Tecnología', 'Suplementación'],
    #     'Medio de pago': ['Crédito', 'Débito'],
    #     'Prueba': ['ntoareu']
    # }

    # print(gdrive.actualize_format(gdrive.get_files('Formatos')[0][1], 'Listas', data_dict))
    print(gdrive.read_sheet_as_dataframe('Formato 1', 'Compras-Gastos'))

