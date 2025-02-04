import requests
import json
import streamlit as st
import pandas as pd

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
def reporte_venta():
    venta=[
        '1',
        '1',
        '1',
        '1',
        '1'
        ]
    append_data(venta,st.secrets['ids']['repo_ventas'])
if st.button('guardar'):
    reporte_venta()
    st.rerun()
ventas=load_data(st.secrets['urls']['repo_ventas'])
st.write(ventas)