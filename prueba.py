import streamlit as st
import datetime as dt
import pandas as pd
import login

cobranzas=login.load_data(st.secrets['urls']['cobranzas'])
# Suponiendo que 'vencimiento' es una columna con strings de fechas
cobranzas['vencimiento'] = pd.to_datetime(cobranzas['vencimiento'], format="%d-%m-%Y", errors='coerce')

# Si quieres comparar con la fecha de hoy
cobranzas.loc[cobranzas['vencimiento'].dt.date > dt.date.today(), 'estado'] = 'Pendiente de pago'

# Si quieres volver a convertirlas a string para Google Sheets
cobranzas['vencimiento'] = cobranzas['vencimiento'].dt.strftime('%d-%m-%Y')