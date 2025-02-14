import streamlit as st
import login

# Llamar al módulo de login
login.generarLogin()
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

st.title('Reporte general')
prestamos=st.session_state['prestamos']
prestamos=prestamos[prestamos['estado']=='liquidado']
prestamos_vigentes=prestamos.shape[0]
st.write(f'Prestamos vigentes: {prestamos_vigentes}')

clientes=st.session_state["clientes"]
cobranzas=st.session_state["cobranzas"]

moras=cobranzas[cobranzas['estado']=='en mora']
cartones_morosos=prestamos[prestamos['id'].isin(moras['prestamo_id'].unique())]
morosos=clientes[clientes['nombre'].isin(cartones_morosos['nombre'].unique())]
st.write(f'Cantidad de clientes atrasados: {morosos.shape[0]}')


with st.expander('ver movimientos de caja'):
    st.subheader('movimientos de caja')
    st.dataframe(st.session_state["mov"])

with st.expander('reporte de ventas'):
    st.subheader('reporte de ventas')
    st.dataframe(st.session_state['repo_ventas'])