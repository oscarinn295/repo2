import streamlit as st
import login
import pandas as pd

# Llamar al módulo de login
login.generarLogin()

# Ruta al archivo Excel
FILE_PATH = "C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\DB\\Visita.xlsx"

# Función para cargar los datos
def load_data():
    return pd.read_excel(FILE_PATH, engine="openpyxl")

# Función para guardar los datos
def save_data(dataframe):
    dataframe.to_excel(FILE_PATH, index=False, engine="openpyxl")
    st.session_state['visitas']

# Inicializar la base de datos y la página actual
if "visitas" not in st.session_state:
    st.session_state["visitas"] = load_data()

visitas=load_data()
def crear_visitas(data):
    for i in range(data['cantidad']+1):
        nueva_visita={
            'visita':'cobranza',
            'vendedor':st.session_state['usuario'],
            'cliente':data['nombre'],
            'fecha':data['fecha'],
            'notas':''
            }
        visitas=pd.concatenate([visitas,nueva_visita])
    save_data(visitas)


# Función para mostrar la tabla con filtro de búsqueda
def display_table(search_query=""):
    st.subheader("Lista")
    df=load_data()
    # Mostrar tabla en Streamlit
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No se encontraron resultados.")


st.title("Visitas")
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