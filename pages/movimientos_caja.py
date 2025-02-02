import streamlit as st
import login
import pandas as pd
from datetime import date

idc=st.secrets['ids']['flujo_caja']
url=st.secrets['urls']['flujo_caja']
def load():
    return login.load_data(url)
def new(datos):
    login.append_data(idc,datos)
    st.session_state['prestamos']=load()
def save(df):
    login.save_data(idc,df)
    st.session_state['prestamos']=load()

flujo=load()
# Inicializar la base de datos y la página actual


login.generarLogin()


st.session_state["page"] = "main"
if 'mov' not in st.session_state:
    st.session_state['mov']=load()
    

# Función para mostrar la tabla con filtro de búsqueda
def display_table(search_query=""):
    st.subheader("Movimientos Registrados")

    # Filtrar datos según la consulta de búsqueda
    df = st.session_state["mov"]
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]

    if not df.empty:
        st.dataframe(df)  # Usar una tabla simple para mostrar los datos
    else:
        st.warning("No se encontraron resultados.")

# Función para eliminar un movimiento
def delete_client(index):
    st.session_state["mov"].drop(index=index, inplace=True)
    st.session_state["mov"].reset_index(drop=True, inplace=True)  # Reiniciar índices
    save(st.session_state["mov"])
    st.success("Movimiento eliminado.")

# Función para guardar un nuevo movimiento
def guardar_movimiento(data):
    df = st.session_state["mov"]
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    save(df)
    st.session_state["mov"] = df

# Página de lista de movimientos
if st.session_state["page"] == "main":
    st.title("Movimientos de Caja")

    # Botón para crear un nuevo movimiento
    if st.button("Crear Movimiento"):
        st.session_state["page"] = "gestionar_movimiento"
        st.rerun()

    # Barra de búsqueda
    search_query = st.text_input("Buscar movimiento (por cualquier campo)", key="search_query")
    display_table(search_query)

    # Botón para reiniciar datos
    if st.button("Reiniciar datos"):
        st.session_state["mov"] = load()
        st.success("Datos reiniciados.")

# Página de gestión de movimientos
elif st.session_state["page"] == "gestionar_movimiento":
    st.title("Gestión de Movimientos")
    
    # Formulario para crear un movimiento
    with st.form("form_movimiento"):
        fecha = st.date_input("Fecha del Movimiento", value=date.today())
        concepto = st.text_input("Concepto*")
        tipo_movimiento = st.selectbox("Tipo de Movimiento*", ["Seleccione una opción", "Ingreso de Dinero", "Egreso de Dinero"])
        monto = st.number_input("Monto*", min_value=0.0,step=1000.0)
        
        # Botón dentro del formulario
        crear = st.form_submit_button("Guardar")

    if st.button("Volver"):
        st.session_state["page"] = "main"  # Regresar a la página de lista
        st.rerun()  # Forzar la redirección

    # Manejo del evento al enviar el formulario
    if crear:
        if not concepto or tipo_movimiento == "Seleccione una opción":
            st.error("Por favor, complete todos los campos obligatorios marcados con *.")
        else:
            ingreso = monto if tipo_movimiento == "Ingreso de Dinero" else 0.0
            egreso = monto if tipo_movimiento == "Egreso de Dinero" else 0.0
            saldo_anterior = st.session_state["mov"]["Saldo"].iloc[-1] if not st.session_state["mov"].empty else 0.0
            saldo = saldo_anterior + ingreso - egreso
            
            nuevo_movimiento = {
                "Fecha": fecha,
                "Concepto": concepto,
                "Ingreso": ingreso,
                "Egreso": egreso,
                "Total": ingreso - egreso,
                "Saldo": saldo,
            }

            guardar_movimiento(nuevo_movimiento)
            st.success("Movimiento guardado con éxito.")
            st.session_state["page"] = "main"
            st.rerun()
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
