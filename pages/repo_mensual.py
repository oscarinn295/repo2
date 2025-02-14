import login
import pandas as pd
import streamlit as st

# Llamar al módulo de login
login.generarLogin()

idc=st.secrets['ids']['repo_mensual']
url=st.secrets['urls']['repo_mensual']
def load():
    return login.load_data(url)

def new(data):#añade una columna entera de datos
    login.append_data(data,st.secrets['ids']['clientes'])

if 'repo_mensual' not in st.session_state:
    st.session_state['repo_mensual']=load()
# Función para mostrar la tabla con filtro de búsqueda
def display_table(search_query=""):
    st.subheader("Lista de Movimientos")
    df=st.session_state['repo_mensual']
    # Mostrar tabla en Streamlit
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No se encontraron resultados.")


st.title("Reporte Mensual")
display_table()
