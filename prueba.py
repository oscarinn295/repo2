import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd


def authenticate():
    # Definir los alcances de la API
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    # Cargar credenciales desde secrets.toml
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
    return gspread.authorize(creds)

def get_worksheet(sheet_id):
    """Obtiene la hoja de cálculo por su ID"""
    client = authenticate()
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.worksheet("Sheet1")  # Puedes cambiar esto si usas una pestaña específica

def delete_data(id_value,sheet_id ):
    """Elimina una fila según el valor en la columna 'id'"""
    worksheet = get_worksheet(sheet_id)
    cell = worksheet.find(str(id_value))
    if cell:
        worksheet.delete_rows(cell.row)


def save_data(id_value, column_name, new_value,sheet_id):
    """Modifica un valor en una fila según el ID y el nombre de la columna"""
    worksheet = get_worksheet(sheet_id)
    col_labels = worksheet.row_values(1)  # Obtiene la primera fila con los nombres de columnas
    if column_name not in col_labels:
        print("Columna no encontrada")
        return
    col_index = col_labels.index(column_name) + 1  # Convertir a índice basado en 1
    cell = worksheet.find(str(id_value))
    if cell:
        worksheet.update_cell(cell.row, col_index, new_value)


def append_data(new_values,sheet_id):
    """Añade una nueva fila al final del documento"""
    worksheet = get_worksheet(sheet_id)
    worksheet.append_row(new_values)

def load_data(id):
    def get_google_sheet(spreadsheet_id, range_name):
        """Obtiene datos de una hoja de Google Sheets."""
        client = authenticate()
        sheet = client.open_by_key(spreadsheet_id).worksheet(range_name)
        return sheet.get_all_values()

    def gsheet2df(sheet_data):
        """Convierte los datos obtenidos de Google Sheets en un DataFrame de Pandas."""
        if not sheet_data:
            st.error("No se encontraron datos en la hoja.")
            return pd.DataFrame()
        
        header = sheet_data[0]  # Primera fila como encabezado
        values = sheet_data[1:]  # Datos sin el encabezado
        df = pd.DataFrame(values, columns=header)
        return df

    # Configuración de la hoja
    SPREADSHEET_ID = id
    RANGE_NAME = 'Sheet1'

    # Obtener datos y convertirlos en DataFrame
    sheet_data = get_google_sheet(SPREADSHEET_ID, RANGE_NAME)
    return gsheet2df(sheet_data)
st.session_state['clientes']=load_data(st.secrets['prueba_ids']['clientes'])
def delete(index):
    delete_data(index,st.secrets['prueba_ids']['clientes'])
def save(id,column,data):
    save_data(id,column,data,st.secrets['prueba_ids']['clientes'])
def new(data):
    append_data(data,st.secrets['prueba_ids']['clientes'])
if st.button('modificar'):
    mod='molinas'
    save(0,'nombre',mod)
    st.rerun()
if st.button('borrar'):
    delete('0')
    st.rerun()
if st.button('añadir'):
    nuevo=['0',
           'molinas, oscar alexander',
           'test',
           '0',
           'coso',
           '18-03-2025',
           '39196960',
           '3794273525',
           'example@gmail.com']
    new(nuevo)
    st.rerun()
st.dataframe(st.session_state['clientes'])