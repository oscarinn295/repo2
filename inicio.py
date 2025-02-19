import streamlit as st
st.set_page_config(layout='wide')
import login
import pandas as pd
st.title("Pagina administrativa de GrupoGon!")
login.generarLogin()
# Inicializar las bases de datos
if 'usuario' in st.session_state:
    if "clientes" not in st.session_state:
        st.session_state["clientes"] = login.load_data_vendedores(st.secrets['urls']['clientes'])
    if "cobranzas" not in st.session_state:
        st.session_state["cobranzas"] = login.load_data_vendedores(st.secrets['urls']['cobranzas'])
    if "prestamos" not in st.session_state:
        st.session_state["prestamos"] = login.load_data_vendedores(st.secrets['urls']['prestamos'])
    if st.session_state['user_data']['permisos'].iloc[0]=='admin':
        if "mov" not in st.session_state:
            st.session_state["mov"] = login.load_data(st.secrets['urls']['flujo_caja'])
        if 'repo_cobranzas' not in st.session_state:
            st.session_state['repo_cobranzas']=login.load_data(st.secrets['urls']['repo_cobranzas'])
        if 'comisiones' not in st.session_state:
            st.session_state['comisiones']=login.load_data(st.secrets['urls']['repo_comision'])
        if "repo_mensual" not in st.session_state:
            st.session_state["repo_mensual"] = login.load_data(st.secrets['urls']['repo_mensual'])
        if "morosos" not in st.session_state:
            st.session_state["morosos"] = login.load_data(st.secrets['urls']['repo_morosos'])
        if 'repo_ventas' not in st.session_state:
            st.session_state['repo_ventas']=login.load_data(st.secrets['urls']['repo_ventas'])
