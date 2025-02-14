import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
import unicodedata
import numpy as np

# ================================
# Funciones de autenticación y acceso
# ================================
def authenticate():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
    return gspread.authorize(creds)

def get_worksheet(sheet_id):
    client = authenticate()
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.worksheet("Sheet1")  # Cambia "Sheet1" si usas otra pestaña

def overwrite_sheet(new_data, sheet_id):
    """
    Sobrescribe toda la hoja de cálculo con los nuevos datos.
    
    :param new_data: Lista de listas, donde cada sublista representa una fila.
    :param sheet_id: ID de la hoja de cálculo en Google Sheets.
    """
    worksheet = get_worksheet(sheet_id)
    worksheet.clear()  # Borra todo el contenido
    worksheet.update("A1", new_data)  # Escribe los nuevos datos desde A1

# ================================
# Funciones de carga y transformación de datos
# ================================
def load_data(url):
    return pd.read_excel(url, engine='openpyxl')

def quitar_tildes(texto):
    return ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))

# Cargar datos en la sesión si aún no están cargados
if "clientes" not in st.session_state:
    st.session_state["clientes"] = load_data(st.secrets['urls']['clientes'])
if "cobranzas" not in st.session_state:
    st.session_state["cobranzas"] = load_data(st.secrets['urls']['cobranzas'])
if "prestamos" not in st.session_state:
    st.session_state["prestamos"] = load_data(st.secrets['urls']['prestamos'])

clientes = st.session_state["clientes"]
cobranzas = st.session_state["cobranzas"]
prestamos = st.session_state["prestamos"]

# Quitar tildes y limpiar espacios en blanco en el campo 'nombre'
clientes['nombre'] = clientes['nombre'].str.strip().apply(quitar_tildes)
prestamos['nombre'] = prestamos['nombre'].str.strip().apply(quitar_tildes)
cobranzas['nombre'] = cobranzas['nombre'].str.strip().apply(quitar_tildes)

# ================================
# Función para actualizar la hoja de Google Sheets
# ================================
def actualizar_hoja(sheet_id, df):
    """
    Actualiza la hoja de Google Sheets con el contenido del DataFrame.
    
    Se realizan los siguientes pasos:
      1. Verifica que el DataFrame no esté vacío.
      2. Resetea el índice y, si existe una columna 'id', se actualiza.
      3. Convierte las columnas de fecha a string.
      4. Reemplaza valores NaN o None para evitar errores de JSON.
      5. Convierte el DataFrame a lista de listas (encabezados + filas).
      6. Llama a overwrite_sheet para sobrescribir la hoja.
    """
    # 1. Verificar que el DataFrame no esté vacío
    if df.empty:
        st.error("El DataFrame está vacío. No se actualizará la hoja.")
        return

    # 2. Copiar y resetear el índice (y actualizar columna 'id' si existe)
    df_nuevo = df.copy()
    df_nuevo.reset_index(drop=True, inplace=True)
    if 'id' in df_nuevo.columns:
        df_nuevo['id'] = df_nuevo.index

    # 3. Formatear columnas de fecha (si las hubiera)
    for col in df_nuevo.columns:
        if pd.api.types.is_datetime64_any_dtype(df_nuevo[col]):
            df_nuevo[col] = df_nuevo[col].dt.strftime("%Y-%m-%d")

    # 4. Reemplazar valores NaN y None para evitar errores JSON
    df_nuevo.replace([np.nan, None], '', inplace=True)

    # 5. Convertir el DataFrame a lista de listas (encabezados + filas)
    data = [df_nuevo.columns.tolist()] + df_nuevo.values.tolist()

    # 6. Sobrescribir la hoja en Google Sheets
    overwrite_sheet(data, sheet_id)

# ================================
# Botones de actualización en Streamlit
# ================================
if st.button("Actualizar Clientes en Google Sheets"):
    actualizar_hoja(st.secrets['ids']['clientes'], clientes)
    st.success("Clientes actualizados en Google Sheets")

if st.button("Actualizar Prestamos en Google Sheets"):
    actualizar_hoja(st.secrets['ids']['prestamos'], prestamos)
    st.success("Prestamos actualizados en Google Sheets")

if st.button("Actualizar Cobranzas en Google Sheets"):
    actualizar_hoja(st.secrets['ids']['cobranzas'], cobranzas)
    st.success("Cobranzas actualizados en Google Sheets")
