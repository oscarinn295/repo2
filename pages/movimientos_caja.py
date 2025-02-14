import streamlit as st
import login
import pandas as pd
from datetime import date

idc=st.secrets['ids']['flujo_caja']
url=st.secrets['urls']['flujo_caja']
def load():
    return login.load_data(url)
def new(data):#añade una columna entera de datos
    login.append_data(data,idc)

flujo=load()
# Inicializar la base de datos y la página actual


login.generarLogin()

st.session_state["page"] = "main"
if 'mov' not in st.session_state:
    st.session_state['mov']=load()


def crear():
    st.subheader("Gestión de Movimientos")
    fecha = st.date_input("Fecha del Movimiento", value=date.today())
    concepto = st.text_input("Concepto*")
    tipo_movimiento = st.selectbox("Tipo de Movimiento*", ["Seleccione una opción", "Ingreso de Dinero", "Egreso de Dinero"])
    monto = st.number_input("Monto*", min_value=0.0,step=1000.0)

    if st.form_submit_button("Guardar"):
        if not concepto or tipo_movimiento == "Seleccione una opción":
            st.error("Por favor, complete todos los campos obligatorios marcados con *.")
        else:
            ingreso = monto if tipo_movimiento == "Ingreso de Dinero" else 0.0
            egreso = monto if tipo_movimiento == "Egreso de Dinero" else 0.0
            saldo_anterior = st.session_state["mov"]["Saldo"].iloc[-1] if not st.session_state["mov"].empty else 0.0
            saldo = saldo_anterior + ingreso - egreso
            
            nuevo_movimiento = [fecha.strftime('%d/%m/%Y'), concepto,ingreso, egreso,ingreso - egreso, saldo]

            new(nuevo_movimiento)
            st.success("Movimiento guardado con éxito.")

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


