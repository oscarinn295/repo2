import login
import pandas as pd
import streamlit as st


# Llamar al módulo de login
login.generarLogin()


idc=st.secrets['ids']['repo_ventas']
url=st.secrets['urls']['repo_ventas']
def load():
    return login.load_data(url)


# Inicializar la base de datos y la página actual
if "repo_ventas" not in st.session_state:
    st.session_state["repo_ventas"] = load()


# Función para mostrar la tabla con filtro de búsqueda
def display_table(search_query=""):
    st.subheader("Lista de Movimientos")
    df=st.session_state["repo_ventas"]
    # Mostrar tabla en Streamlit
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No se encontraron resultados.")


st.title("Ventas por vendedor")
display_table()
