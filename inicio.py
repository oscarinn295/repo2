import streamlit as st
st.set_page_config(layout='wide')
import login
import pandas as pd
st.title("Pagina administrativa de GrupoGon!")
login.generarLogin()
st.text("Esto es una demo de la nueva página de gestión de clientes y algunos datos financieros.")
st.text("Hecho por Oscar Molinas.")



# Inicializar las bases de datos
if "clientes" not in st.session_state:
    st.session_state["clientes"] = login.load_data(st.secrets['urls']['clientes'])
if "cobranzas" not in st.session_state:
    st.session_state["cobranzas"] = login.load_data(st.secrets['urls']['cobranzas'])
if "mov" not in st.session_state:
    st.session_state["mov"] = login.load_data(st.secrets['urls']['flujo_caja'])
if "prestamos" not in st.session_state:
    st.session_state["prestamos"] = login.load_data(st.secrets['urls']['prestamos'])
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
if 'en_mora' not in st.session_state:
    st.session_state['en_mora']=login.load_data(st.secrets['urls']['en_mora'])
if 'pendiente' not in st.session_state:
    st.session_state['pendiente']=login.load_data(st.secrets['urls']['pendientes'])