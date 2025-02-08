import streamlit as st
st.set_page_config(layout='wide')
import login
import pandas as pd
st.title("Pagina administrativa de GrupoGon!")
login.generarLogin()
# Inicializar las bases de datos
if "clientes" not in st.session_state:
    st.session_state["clientes"] = login.load_data(st.secrets['prueba_urls']['clientes'])
if "cobranzas" not in st.session_state:
    st.session_state["cobranzas"] = login.load_data(st.secrets['prueba_urls']['cobranzas'])
if "mov" not in st.session_state:
    st.session_state["mov"] = login.load_data(st.secrets['prueba_urls']['flujo_caja'])
if "prestamos" not in st.session_state:
    st.session_state["prestamos"] = login.load_data(st.secrets['prueba_urls']['prestamos'])
if 'repo_cobranzas' not in st.session_state:
    st.session_state['repo_cobranzas']=login.load_data(st.secrets['prueba_urls']['repo_cobranzas'])
if 'comisiones' not in st.session_state:
    st.session_state['comisiones']=login.load_data(st.secrets['prueba_urls']['repo_comision'])
if "repo_mensual" not in st.session_state:
    st.session_state["repo_mensual"] = login.load_data(st.secrets['prueba_urls']['repo_mensual'])
if "morosos" not in st.session_state:
    st.session_state["morosos"] = login.load_data(st.secrets['prueba_urls']['repo_morosos'])
if 'repo_ventas' not in st.session_state:
    st.session_state['repo_ventas']=login.load_data(st.secrets['prueba_urls']['repo_ventas'])
if 'en_mora' not in st.session_state:
    st.session_state['en_mora']=login.load_data(st.secrets['prueba_urls']['en_mora'])
if 'pendiente' not in st.session_state:
    st.session_state['pendiente']=login.load_data(st.secrets['prueba_urls']['pendientes'])
