import login
import pandas as pd
import streamlit as st


# Llamar al módulo de login
login.generarLogin()

idc=st.secrets['ids']['repo_morosos']
url=st.secrets['urls']['repo_morosos']
def load():
    return login.load_data(url)

if 'morosos' not in st.session_state:
    st.session_state['morosos']=load()

# Función para mostrar la tabla con filtro de búsqueda
def display_table(search_query=""):
    st.subheader("Lista de Movimientos")
    df=st.session_state['morosos']
    # Mostrar tabla en Streamlit
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No se encontraron resultados.")


st.title("Morosos")
display_table()
