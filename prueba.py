import requests
import json
import streamlit as st
import pandas as pd

# Cargar valores desde secrets.toml
api = st.secrets["api"]['dfs']
def load_data(URL):
    return pd.read_excel(URL)

def save_data(id: str, datos):
    """
    Sobrescribe toda la hoja con nuevos datos.
    """
    values = datos.values.tolist()
    values.insert(0, datos.columns.tolist())  # Agrega encabezados

    payload = {
        "fileId": id,
        "values": values,
        "all": True  # Sobrescribir toda la hoja
    }
    response = requests.post(api, data=json.dumps(payload, default=str))
    
    return response.json()

import login
import pandas as pd
import streamlit as st

idc=st.secrets['ids']['prestamos']
url=st.secrets['urls']['prestamos']
clientes=login.load_data(st.secrets['urls']['clientes'])

def load():
    return load_data(url)

def save(df):
    save_data(idc,df)
    st.session_state['prestamos']=load()
if 'prestamos' not in st.session_state:
    st.session_state['prestamos']=load()
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

nuevo_prestamo = pd.DataFrame([{
            "nro": max(st.session_state['prestamos']['nro'], default=0) + 1,
            "fecha": fecha,
            "nombre": nombre_cliente,
            "cantidad": cantidad_cuotas,
            "capital": capital,
            "tipo": tipo_prestamo,
            "estado": estado,
            "vence dia": venc_dia,
            "asociado": producto_asociado,
            "tnm": TNM,
            "monto": monto,
            "obs": obs
        }])
if st.button('guardar'):
    st.session_state["prestamos"] = pd.concat([st.session_state["prestamos"], nuevo_prestamo], ignore_index=True)
    save(st.session_state["prestamos"])
    st.rerun()
st.write(st.session_state["prestamos"])
