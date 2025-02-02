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