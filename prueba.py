import requests
import json
import streamlit as st
import pandas as pd

# Cargar valores desde secrets.toml
api = st.secrets["api"]['dfs']
def load_data(URL):
    return pd.read_excel(URL)

import login

idc=st.secrets['ids']['prestamos']
url=st.secrets['urls']['prestamos']
clientes=login.load_data(st.secrets['urls']['clientes'])

def load():
    return load_data(url)

if 'prestamos' not in st.session_state:
    st.session_state['prestamos']=load()
# Función para insertar datos SIN especificar columna ni fila
def insert_data_without_col(data:list,ID):
    # Datos a insertar
    payload = {
        "fileId":ID,
        "values": [data]
    }

    # Enviar solicitud POST
    response = requests.post(api, data=json.dumps(payload))
    print(response.json())  # Mostrar respuesta del servidor
def new(data:list):
    insert_data_without_col(data,idc)
fecha=''
nombre_cliente = 1
venc_dia='lunes'
producto_asociado=''
estado = ''
tipo_prestamo = ''
cantidad_cuotas = 2
capital =2
TNM=2
monto=2
obs=''

nuevo_prestamo = [
    max(st.session_state['prestamos']['nro'],default=0) + 1,
    fecha,
    nombre_cliente,
    cantidad_cuotas,
    capital,
    tipo_prestamo,
    estado,
    venc_dia,
    producto_asociado,
    TNM,
    monto,
    obs,]
if st.button('guardar'):
    new(nuevo_prestamo)
    st.rerun()
st.session_state["prestamos"]=load()
st.write(st.session_state["prestamos"])