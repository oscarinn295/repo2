import streamlit as st
import pandas as pd
from datetime import datetime, date
import login
# Función para ordenar cobranzas
# Función para ordenar cobranzas
def ordenar_cobranzas(df):
    # Convertimos la columna 'vencimiento' a formato datetime
    df['vencimiento'] = pd.to_datetime(df['vencimiento'], format='%d-%m-%Y', errors='coerce')

    # Definimos la fecha de hoy
    hoy = pd.Timestamp(date.today())

    # Creamos una clave de orden basada en las reglas definidas
    condiciones = [
        (df['vencimiento'] >= hoy),  # Fechas desde hoy en adelante
        (df['vencimiento'] < hoy) & (df['estado'] == 'Pendiente de pago'),  # Anteriores a hoy y pendientes de pago
        (df['estado'] == 'Pago parcial'),  # Pago parcial
        (df['estado'] == 'En mora'),  # En mora
        (df['estado'] == 'Pago total')  # Pago total
    ]

    valores_orden = [0, 2, 3, 4, 5]  # Cambio: Ponemos las fechas futuras con orden 0

    df['orden_estado'] = 6  # Valor por defecto (para evitar problemas)

    for condicion, valor in zip(condiciones, valores_orden):
        df.loc[condicion, 'orden_estado'] = valor

    # Ordenamos por orden_estado y fecha de vencimiento ascendente
    df_sorted = df.sort_values(by=['orden_estado', 'vencimiento'], ascending=[True, True])

    # Eliminamos la columna auxiliar de ordenamiento
    df_sorted = df_sorted.drop(columns=['orden_estado'])
    df_sorted['vencimiento'] = df_sorted['vencimiento'].dt.strftime('%d-%m-%Y')

    return df_sorted


prestamos=login.load_data(st.secrets['urls']['prestamos'])
# Definir función de recálculo
def calcular_recargo(cobranza):
    prestamo = prestamos[prestamos['id'] == cobranza['prestamo_id']]
    
    # Si el préstamo no existe, mantener los valores originales
    if pd.isna(cobranza['prestamo_id']) or prestamo.empty:
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']], 
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])

    vencimiento = prestamo['vence'].iloc[0]
    
    tipo_prestamo = {
        'Mensual: 1-10': 300,
        'Mensual: 10-20': 300,
        'Mensual: 20-30': 300,
        'Quincenal': 500,
        'Semanal: lunes': 400,
        'Semanal: martes': 400,
        'Semanal: miercoles': 400,
        'Semanal: jueves': 400,
        'Semanal: viernes': 400,
        'Semanal: sabado': 400,
        'indef': 0
    }
    
    hoy = pd.Timestamp(date.today())

    # Si no hay fecha de vencimiento, mantener valores originales
    if pd.isna(vencimiento):
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']], 
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])

    dias_mora = (hoy - pd.to_datetime(cobranza['vencimiento'])).days

    # Si la fecha es futura o el estado es "Pago total", mantener los valores originales
    if dias_mora <= 0 or cobranza['estado'] == 'Pago total':
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']], 
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])

    # Si hay mora, calcular los intereses
    interes = tipo_prestamo.get(prestamo['vence'].iloc[0], 0)  # Asegurar que toma el tipo correcto
    interes_por_mora = interes * max(0, dias_mora)
    monto_recalculado_mora = cobranza['monto'] + interes_por_mora

    return pd.Series([dias_mora, interes_por_mora, monto_recalculado_mora], 
                     index=['dias_mora', 'mora', 'monto_recalculado_mora'])