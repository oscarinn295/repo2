import login
import pandas as pd
import streamlit as st


# Llamar al módulo de login
login.generarLogin()

idc=st.secrets['ids']['repo_morosos']
url=st.secrets['urls']['repo_morosos']
def load():
    return login.load_data(url)
def new(datos):
    login.append_data(idc,datos)
    st.session_state['prestamos']=load()
def save(df):
    login.save_data(idc,df)
    st.session_state['prestamos']=load()
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


st.title("Morosos, faltan datos!!!!")
display_table()

if st.session_state['usuario']=="admin":
    st.title("subir nuevos datos")
    #concatenar o sobreescribir
    # Título de la aplicación
    st.title("Cargar y analizar archivo CSV")

    # Widget para cargar el archivo
    uploaded_file = st.file_uploader("Sube un archivo CSV", type="csv")

    if uploaded_file is not None:
        # Leer el archivo CSV
        df = pd.read_csv(uploaded_file)

        # Mostrar un mensaje de éxito
        st.success("Archivo cargado con éxito!")

        # Mostrar los datos
        st.subheader("Vista previa de los datos:")
        st.dataframe(df.head())  # Muestra las primeras filas

        # Mostrar información adicional del DataFrame
        st.subheader("Descripción estadística:")
        st.write(df.describe())

        # Mostrar las columnas disponibles
        st.subheader("Columnas del archivo:")
        st.write(df.columns.tolist())

    else:
        st.info("Por favor, sube un archivo para comenzar.")