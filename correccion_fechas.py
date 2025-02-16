import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
import gspread.utils  # Para convertir (fila, columna) a notación A1
# Ocultar el botón de Deploy con CSS
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

def authenticate():
    """Autentica con Google Sheets y guarda el cliente en la sesión."""
    if "gspread_client" not in st.session_state:
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )
        st.session_state["gspread_client"] = gspread.authorize(creds)

def get_worksheet(sheet_id):
    """Obtiene la hoja 'Sheet1' de la hoja de cálculo indicada."""
    authenticate()
    client = st.session_state["gspread_client"]
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.worksheet("Sheet1")

def update_sheet(new_data, sheet_id):
    """
    Actualiza solo el rango correspondiente a new_data sin borrar el resto de la hoja.
    
    :param new_data: Lista de listas (la primera fila debería ser los encabezados).
    :param sheet_id: ID de la hoja de cálculo.
    """
    worksheet = get_worksheet(sheet_id)
    # Determinar la dimensión de los datos nuevos
    num_rows = len(new_data)
    num_cols = len(new_data[0]) if num_rows > 0 else 0
    # Definir el rango de actualización (por ejemplo, "A1:E10")
    end_cell = gspread.utils.rowcol_to_a1(num_rows, num_cols)
    worksheet.update(f"A1:{end_cell}", new_data)

# ----- PROCESAMIENTO DE DATOS -----

import login  # Se asume que login.load_data devuelve un DataFrame

# Cargar datos
cobranzas = login.load_data(st.secrets['urls']['cobranzas'])

def format_dates(df, column_name):
    """Convierte las fechas del formato '%Y-%m-%d' a '%d-%m-%Y' en la columna indicada."""
    df[column_name] = pd.to_datetime(df[column_name], format='%Y-%m-%d').dt.strftime('%d-%m-%Y')
    return df

# Aplicar el formateo a la columna 'vencimiento'
df = format_dates(cobranzas, 'vencimiento')

# Reemplazar los NaN por cadenas vacías para evitar errores de JSON
df = df.fillna("")

# Convertir el DataFrame a lista de listas (incluyendo los encabezados)
data_to_upload = [df.columns.tolist()] + df.values.tolist()

# Actualizar la hoja: solo se sobreescriben las celdas desde A1 hasta la última celda de data_to_upload.
update_sheet(data_to_upload, st.secrets['ids']['cobranzas'])
