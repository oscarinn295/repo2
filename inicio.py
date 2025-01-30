import streamlit as st
import login
st.title("Pagina administrativa de GrupoGon!")
login.generarLogin()
st.text("Esto es una demo de la nueva página de gestión de clientes y algunos datos financieros.")
st.text("Acá ya está replicada toda la información de la vieja página, excepto de los morosos.")
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
if 'visitas' not in st.session_state or not isinstance(st.session_state['visitas'], pd.DataFrame):
    st.session_state['visitas'] = login.load_data(st.secrets['urls']['visitas'])