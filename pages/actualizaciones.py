import streamlit as st
import login
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
#plata en la calle
#plata por cobrar este mes
#numero de clientes por vendedor
#numero de cobranzas pendientes por mes, por vendedor y estado de las cobranzas
#todos los morosos
