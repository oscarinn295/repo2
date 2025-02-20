import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime

# Ocultar el botón de Deploy con CSS
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Autenticación con Google Sheets
def authenticate():
    if "gspread_client" not in st.session_state:
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
        st.session_state["gspread_client"] = gspread.authorize(creds)

def get_worksheet(sheet_id):
    authenticate()
    client = st.session_state["gspread_client"]
    return client.open_by_key(sheet_id).worksheet("Sheet1")

def overwrite_sheet(data, sheet_id):
    worksheet = get_worksheet(sheet_id)
    worksheet.clear()
    worksheet.update("A1", data)

# Cargar datos
def load_data(url):
    return pd.read_excel(url, engine='openpyxl')

prestamos = load_data(st.secrets['urls']['prestamos'])
cobranzas = load_data(st.secrets['urls']['cobranzas_prueba'])

# Preparar datos
prestamos['id'] = prestamos['id'].astype(str)
cobranzas['prestamo_id'] = cobranzas['prestamo_id'].astype(str)
cobranzas['vencimiento'] = pd.to_datetime(cobranzas['vencimiento'], format='%d-%m-%Y', errors='coerce')

hoy_date = date.today()

# Actualizar estado de cobranzas
cobranzas['estado'] = np.where(
    cobranzas['vencimiento'].dt.date >= hoy_date, 'Pendiente de pago',
    np.where((cobranzas['estado'] == 'Pendiente de pago'), 'En mora', cobranzas['estado'])
)

# Calcular recargos por mora
def calcular_recargo(cobranza):
    if cobranza['estado'] in ['Pago total', 'Pendiente de pago']:
        return cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']
    
    monto = pd.to_numeric(cobranza['monto'], errors='coerce') or 0.0
    prestamo = prestamos[prestamos['id'] == cobranza['prestamo_id']]
    
    if prestamo.empty or pd.isna(cobranza['vencimiento']):
        return cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']
    
    tipo_prestamo = {
        'Mensual: 1-10': 500, 'Mensual: 10-20': 500, 'Mensual: 20-30': 500,
        'Quincenal': 400, 'Semanal: lunes': 300, 'Semanal: martes': 300,
        'Semanal: miercoles': 300, 'Semanal: jueves': 300, 'Semanal: viernes': 300,
        'Semanal: sabado': 300, 'indef': 0
    }
    
    dias_mora = max((datetime.today() - cobranza['vencimiento']).days, 0)
    tipo = prestamo['vence'].iloc[0]
    interes = tipo_prestamo.get(tipo, 0)
    
    mora = interes * dias_mora
    monto_recalculado = monto + mora
    
    return dias_mora, mora, monto_recalculado

# Botón para calcular recargos
if st.button('Calcular recargos por mora'):
    cobranzas[['dias_mora', 'mora', 'monto_recalculado_mora']] = cobranzas.apply(
        calcular_recargo, axis=1, result_type='expand'
    )
    
    column_order = [
        'id', 'prestamo_id', 'entregado', 'tnm', 'cantidad de cuotas',
        "vendedor", "nombre", "n_cuota", "monto", "vencimiento", 
        "dias_mora", "mora", 'capital', 'cuota pura', 'intereses',
        'amortizacion', 'iva', 'monto_recalculado_mora', 'pago', 'estado', 
        'medio de pago', 'cobrador', 'fecha_cobro'
    ]
    
    cobranzas = cobranzas[column_order].replace({np.nan: "", pd.NaT: ""})
    cobranzas['vencimiento'] = pd.to_datetime(cobranzas['vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y').fillna("")
    cobranzas['fecha_cobro'] = pd.to_datetime(cobranzas['fecha_cobro'], errors='coerce').dt.strftime('%d-%m-%Y').fillna("")
    
    data_to_upload = [cobranzas.columns.tolist()] + cobranzas.astype(str).values.tolist()
    sheet_id = st.secrets['ids']['cobranzas']
    
    try:
        overwrite_sheet(data_to_upload, sheet_id)
        st.success("Datos actualizados correctamente.")
    except Exception as e:
        st.error(f"Error al subir los datos: {e}")
