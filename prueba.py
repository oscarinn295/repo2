import streamlit as st
import datetime as dt
import pandas as pd
import login
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

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
    if "gspread_client" not in st.session_state:
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
        st.session_state["gspread_client"] = gspread.authorize(creds)

def get_worksheet(sheet_id):
    authenticate()
    client = st.session_state["gspread_client"]
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.worksheet("Sheet1")

def overwrite_sheet(new_data, sheet_id):
    worksheet = get_worksheet(sheet_id)
    worksheet.clear()
    worksheet.update("A1", new_data)

def load_data(url):
    return pd.read_excel(url, engine='openpyxl')

# Cargar datos de préstamos y cobranzas
prestamos = login.load_data(st.secrets['urls']['prestamos'])
cobranzas = login.load_data(st.secrets['urls']['cobranzas'])

# Aseguramos que los IDs sean del mismo tipo (cadena)
prestamos['id'] = prestamos['id'].astype(str)
cobranzas['prestamo_id'] = cobranzas['prestamo_id'].astype(str)

# Convertir la columna 'vencimiento' a datetime para trabajar con fechas
cobranzas['vencimiento'] = pd.to_datetime(cobranzas['vencimiento'], format='%d-%m-%Y', errors='coerce')

# Definir la fecha de hoy
hoy_date = dt.date.today()

# Actualizar el estado:
# • Si el vencimiento es hoy o en el futuro, se deja como "Pendiente de pago".
# • Si el vencimiento es anterior a hoy y el estado es "Pendiente de pago", se transforma a "En mora".
# • Para "Pago total" se conservan los valores que ya tenías.
cobranzas.loc[cobranzas['vencimiento'].dt.date >= hoy_date, 'estado'] = 'Pendiente de pago'
cobranzas.loc[(cobranzas['vencimiento'].dt.date < hoy_date) & (cobranzas['estado'] == 'Pendiente de pago'), 'estado'] = 'En mora'

# Convertir nuevamente 'vencimiento' a string para subirlo (si es necesario)
cobranzas['vencimiento'] = cobranzas['vencimiento'].dt.strftime('%d-%m-%Y')

def calcular_recargo(cobranza):
    """
    Para cada cobranza:
      - Si el estado es "Pago total": se conservan los valores ya existentes.
      - Si el estado es "Pendiente de pago": no se modifica (se asume que el vencimiento aún no pasó).
      - Solo para las cobranzas en "En mora" se recalculan:
            * Los días de mora (solo positivos).
            * El interés acumulado, multiplicando la tasa diaria por los días de mora.
            * El monto recalculado sumando el monto original + interés acumulado.
    """
    # No recalcular si está en "Pago total"
    if cobranza['estado'] == 'Pago total':
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']],
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])
    
    # Para las cobranzas que siguen en "Pendiente de pago", no se modifica nada.
    if cobranza['estado'] == 'Pendiente de pago':
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']],
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])
    
    # Convertir monto a float (si no puede, se usa 0)
    try:
        monto = float(cobranza['monto'])
    except:
        monto = 0.0

    # Buscar el préstamo correspondiente
    prestamo = prestamos[prestamos['id'] == cobranza['prestamo_id']]
    if pd.isna(cobranza['prestamo_id']) or prestamo.empty:
        # Si no se encontró, se mantienen los valores existentes
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']],
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])

    # Diccionario con tasas de interés diarias
    tipo_prestamo = {
        'Mensual: 1-10': 500,
        'Mensual: 10-20': 500,
        'Mensual: 20-30': 500,
        'Quincenal': 400,
        'Semanal: lunes': 300,
        'Semanal: martes': 300,
        'Semanal: miercoles': 300,
        'Semanal: jueves': 300,
        'Semanal: viernes': 300,
        'Semanal: sabado': 300,
        'indef': 0
    }
    
    # Convertir la fecha de vencimiento de la cobranza a datetime
    cobranza_vencimiento = pd.to_datetime(cobranza['vencimiento'], format='%d-%m-%Y', errors='coerce')
    if pd.isna(cobranza_vencimiento):
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']],
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])
    
    hoy_ts = pd.Timestamp(date.today())
    dias_mora = (hoy_ts - cobranza_vencimiento).days

    # Si el número de días de mora es menor o igual a 0 (lo que indicaría que no está vencida)
    # se mantienen los valores originales
    if dias_mora <= 0:
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']],
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])
    
    # Obtener el tipo de préstamo y la tasa (se asume que el valor en la columna es idéntico a las claves del diccionario)
    tipo = prestamo['vence'].iloc[0]
    interes = tipo_prestamo.get(tipo)

    interes_por_mora = interes * dias_mora
    monto_recalculado = monto + interes_por_mora

    return pd.Series([dias_mora, interes_por_mora, monto_recalculado],
                     index=['dias_mora', 'mora', 'monto_recalculado_mora'])

if st.button('calcular recargos por mora'):
    # Recargar datos (en caso de que hayan cambiado)
    cobb = login.load_data(st.secrets['urls']['cobranzas'])
    
    # Asegurar que el campo de ID se trate como cadena y convertir la fecha de vencimiento
    cobb['prestamo_id'] = cobb['prestamo_id'].astype(str)
    cobb['vencimiento'] = pd.to_datetime(cobb['vencimiento'], format='%d-%m-%Y', errors='coerce')
    
    # Actualizar el estado de las cobranzas:
    # • Si el vencimiento es hoy o en el futuro, se deja "Pendiente de pago".
    # • Si el vencimiento es anterior a hoy y aún está en "Pendiente de pago", se cambia a "En mora".
    cobb.loc[cobb['vencimiento'].dt.date >= hoy_date, 'estado'] = 'Pendiente de pago'
    cobb.loc[(cobb['vencimiento'].dt.date < hoy_date) & (cobb['estado'] == 'Pendiente de pago'), 'estado'] = 'En mora'
    
    # Aplicar la función de recálculo solo a aquellas cobranzas que estén en "En mora"
    cobb[['dias_mora', 'mora', 'monto_recalculado_mora']] = cobb.apply(calcular_recargo, axis=1)
    
    # Ordenar las columnas según el formato requerido
    column_order = ['id', 'prestamo_id', 'entregado', 'tnm', 'cantidad de cuotas',
                    "vendedor", "nombre", "n_cuota", "monto", "vencimiento", 
                    "dias_mora", "mora", 'capital', 'cuota pura', 'intereses',
                    'amortizacion', 'iva', 'monto_recalculado_mora', 'pago', 'estado', 
                    'medio de pago', 'cobrador', 'fecha_cobro']
    cobb = cobb[column_order]
    
    # Reemplazar NaN y valores nulos
    cobb = cobb.replace({np.nan: "", pd.NaT: ""})
    cobb['vencimiento'] = pd.to_datetime(cobb['vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y')
    
    cobb['fecha_cobro'] = pd.to_datetime(cobb['fecha_cobro'], errors='coerce')
    cobb['fecha_cobro'] = cobb['fecha_cobro'].dt.strftime('%d-%m-%Y').fillna("")
    cobb['fecha_cobro'] = cobb['fecha_cobro'].replace("NaT", "")
    
    data_to_upload = [cobb.columns.tolist()] + cobb.astype(str).values.tolist()
    sheet_id = st.secrets['ids']['cobranzas']
    login.overwrite_sheet(data_to_upload, sheet_id)
