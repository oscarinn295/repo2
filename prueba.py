import requests
import json
import streamlit as st
import pandas as pd
from datetime import datetime
import datetime as dt
from dateutil.relativedelta import relativedelta

# Cargar valores desde secrets.toml
api = st.secrets["api"]['dfs']
def load_data(URL):
    return pd.read_excel(URL)

def append_data(data:list,ID):
    # Datos a insertar
    payload = {
        "fileId":ID,
        "values": [data]
    }

    requests.post(api, data=json.dumps(payload))

#gestionar prestamos, funciones
def generar_fechas_prestamos(fecha_registro:str, frecuencia:str, cuotas:int,vencimiento=None):
    """
    Genera fechas de pago a partir de las condiciones dadas.
    :param fecha_registro: que originalmente es un datetime pero como que no me estaba dejando guardar datetime
        así que primero son los strings que salen de eso
        los string de fecha para este caso tienen que venir con este formato %d/%m/%Y
    :param frecuencia: Frecuencia de pago ('semanal', 'quincenal', 'mensual')
    :param cuotas: Número de cuotas
    :vencimiento:10, 20 o 30
    :return: Lista de fechas de pago (list of datetime.date)
    """
    fecha_registro=datetime.strptime(fecha_registro, "%d/%m/%Y")
    fecha_actual=fecha_registro
    fechas=[]
    if frecuencia=='mensual':
        if vencimiento is not None:
            if int(fecha_registro.dt.day())<vencimiento:
                fecha_objetivo=fecha_registro+ dt.timedelta(days=vencimiento-fecha_registro.dt.day())
            elif int(fecha_registro.dt.day())>vencimiento:
                fecha_objetivo=fecha_registro+relativedelta(months=1)- dt.timedelta(days=fecha_registro.dt.day()-vencimiento)
        else:
            fecha_objetivo=fecha_registro+relativedelta(months=1)
        for _ in range(cuotas):
            fechas.append(fecha_objetivo.strftime("%d/%m/%Y"))
            fecha_objetivo+=relativedelta(months=1)
    elif frecuencia=='quincenal':
        for _ in range(cuotas):
            fecha_actual+=dt.timedelta(weeks=2)
            fechas.append(fecha_actual.strftime("%d/%m/%Y"))
    elif frecuencia=='semanal':
        for _ in range(int(cuotas)):
            fecha_actual+=dt.timedelta(weeks=1)
            fechas.append(fecha_actual.strftime("%d/%m/%Y"))
    return fechas

def crear_cobranzas(data,vencimiento=None):
    st.session_state['cobranzas']=load_data(st.secrets['urls']['cobranzas'])
    fechas=generar_fechas_prestamos(data[1],data[5], data[3],vencimiento)
    i=0
    for fecha in fechas:
        if type(fecha)==str:
            fecha=datetime.strptime(fecha, "%d/%m/%Y")
        nueva_cobranza=[
            int(st.session_state['cobranzas']['id'].max()+1)+i,
            'test',
            data[2],
            i,
            data[10],
            data[10],
            0.0,
            0.0,
            fecha.strftime("%d/%m/%Y"),
            'Pendiente de Pago'
            ]
        i+=1
        append_data(nueva_cobranza,st.secrets['ids']['cobranzas'])
        
nuevo_prestamo = [
            0,
            '04/02/2025',
            'si',
            10,
            1000000,
            'mensual',
            'liquidado',
            20,
            'coso',
            18,
            100000,
            '']
data=nuevo_prestamo
if st.button('guardar'):
    crear_cobranzas(data)
    st.rerun()
cobranzas=load_data(st.secrets['urls']['cobranzas'])
st.write(cobranzas)