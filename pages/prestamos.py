import streamlit as st
import login
import pages.visitas as visitas
import pages.cobranzas as cobranzas
import pages.movimientos_caja as caja
import pandas as pd
# Llamar al módulo de login
login.generarLogin()
import os
from datetime import date

# Ruta del archivo Excel
PATH = "C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\DB\\Prestamo.xlsx"
path_clientes="C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\DB\\clientes.xlsx"
clientes=pd.read_excel(path_clientes, engine="openpyxl")
# Función para cargar datos
def load_data():
    try:
        if os.path.exists(PATH):
            return pd.read_excel(PATH, engine="openpyxl")
        else:
            return pd.DataFrame(columns=['fecha', "nombre", "cantidad", "capital", "tipo", "estado"])
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame(columns=['fecha', "nombre", "cantidad", "capital", "tipo", "estado"])

# Función para guardar datos
def save_data(dataframe):
    try:
        dataframe.to_excel(PATH, index=False, engine="openpyxl")
        st.session_state["prestamos"]=dataframe
    except Exception as e:
        st.error(f"Error al guardar los datos: {e}")

# Inicializar archivo si no existe
if not os.path.exists(PATH):
    df = pd.DataFrame(columns=['fecha', "nombre", "cantidad", "capital", "tipo", "estado"])
    save_data(df)


st.session_state["page"] = "prestamo"  # Página por defecto
if "prestamos" not in st.session_state:
    st.session_state["prestamos"] = load_data()

def display_table(search_query=""):
    st.subheader("Préstamos Registrados")

    df = st.session_state["prestamos"]

    # Filtrar datos según la consulta de búsqueda
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]

    if not df.empty:
        updated_rows = []  # Para almacenar cambios de estado temporalmente
        for index, row in df.iterrows():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(
                    f"**Fecha:** {row['fecha']} | **Cliente:** {row['nombre']} | "
                    f"**Capital:** {row['capital']}"
                )
            with col2:
                if st.button(f"Editar", key=f"editar_{index}"):
                    st.session_state["nro"] = index
                    st.session_state["page"] = "gestionar_prestamo"
                    st.rerun()
            with col3:
                new_estado = st.selectbox(
                    "Estado*", 
                    ["Seleccione una opción", "pendiente", "aceptado", "liquidado", 
                     "al dia", "en mora", "en juicio", "cancelado", "finalizado"],
                    index=["Seleccione una opción", "pendiente", "aceptado", "liquidado",
                           "al dia", "en mora", "en juicio", "cancelado", "finalizado"].index(row["estado"]),
                    key=f"estado_{index}"
                )
                # Agregar cambios si el estado cambió
                if new_estado != row["estado"]:
                    updated_rows.append((index, new_estado))

        # Actualizar los cambios en el DataFrame
        for index, new_estado in updated_rows:
            st.session_state["prestamos"].loc[index, "estado"] = new_estado
            save_data(st.session_state["prestamos"])  # Guardar cambios al archivo Excel
    else:
        st.warning("No se encontraron resultados.")




# Función para guardar un nuevo préstamo
def guardar_prestamo(data):
    df = st.session_state["prestamos"]
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    save_data(df)
    st.session_state["prestamos"] = df

    cobranzas.crear_cobranzas(data)
    visitas.crear_visitas(data)
    caja.prestamo(data)

# Página de lista de préstamos
if st.session_state["page"] == "prestamo":
    st.title("Gestión de Préstamos")

    # Botón para crear un nuevo préstamo
    if st.button("Crear Préstamo"):
        st.session_state["nro"] = None  # No se está editando ningún cliente
        st.session_state["page"] = "gestionar_prestamo"
        st.rerun()

    # Barra de búsqueda
    search_query = st.text_input("Buscar cliente (por cualquier campo)", key="search_query")
    display_table(search_query)

    # Botón para reiniciar datos
    if st.button("Reiniciar datos"):
        st.session_state["prestamos"] = load_data()
        st.success("Datos reiniciados.")

# Página de gestión de préstamos
elif st.session_state["page"] == "gestionar_prestamo":
    st.title("Crear Prestamo")

    # Si estamos editando un préstamo, cargar datos existentes
    if st.session_state["nro"] is not None:
        prestamo = st.session_state["prestamos"].iloc[st.session_state["nro"]]
        fecha = pd.to_datetime(prestamo["fecha"]).date() if prestamo["fecha"] else date.today()
        nombre_cliente = prestamo["nombre"]
        capital = prestamo["capital"]
        tipo_prestamo = prestamo["tipo"]
        cantidad_cuotas = prestamo["cantidad"]
        estado = prestamo["estado"]
    else:
        # Valores por defecto para un nuevo préstamo
        fecha = date.today()
        nombre_cliente = ""
        capital = 0.0
        tipo_prestamo = "Mensual"
        cantidad_cuotas = 1
        estado = "liquidado"

    # Formulario para crear o editar un préstamo
    with st.form("form_prestamo"):
        col1, col2 = st.columns(2)

        with col1:
            nombre_cliente = st.selectbox('Cliente',(nombre for nombre in clientes['nombre']))
            venc_dia=st.selectbox('Dia Vencimiento Cuota',("Seleccione una opción",'Lunes','Martes','Miercoles','Jueves','Viernes','Sabado'))
            producto_asociado=st.text_input('Producto Asociado*')
            estado = st.selectbox("Estado*", ["Seleccione una opción", "pendiente","aceptado","liquidado","al dia","en mora","en juicio","cancelado","finalizado"], index=["Seleccione una opción", "pendiente","aceptado","liquidado","al dia","en mora","en juicio","cancelado","finalizado"].index(estado))
            tipo_prestamo = st.radio("Tipo de Préstamo*", ["Mensual", "Quincenal", "Semanal"], index=["Mensual", "Quincenal", "Semanal"].index(tipo_prestamo))
            
        with col2:
            cantidad_cuotas = st.number_input("Cantidad de Cuotas*", min_value=1, step=1, value=cantidad_cuotas)
            capital = st.number_input("Capital*", min_value=0.0, step=1000.0, value=float(capital))
            TNM=st.number_input('T.N.M*', min_value=0.0, step=0.1)
            monto=st.number_input('Monto Cuota')
        obs=st.text_input('Observaciones')
        # Botón de acción dentro del formulario
        crear = st.form_submit_button("Crear")

    # Botón para volver a la lista de clientes
    if st.button("Cancelar"):
        st.session_state["page"] = "lista"  # Regresar a la página de lista
        st.rerun()  # Forzar la redirección
    # Manejo del evento al enviar el formulario
    if crear:
        if not nombre_cliente or estado == "Seleccione una opción":
            st.error("Por favor, complete todos los campos obligatorios marcados con *.")
        else:
            nuevo_prestamo = {
                "fecha": fecha,
                "nombre": nombre_cliente,
                "cantidad": cantidad_cuotas,
                "capital": capital,
                "tipo": tipo_prestamo,
                "estado": estado,
                "vence dia": venc_dia,
                "asociado": producto_asociado,
                "tnm": TNM,
                "monto": monto,
                "obs": obs
            }
            if st.session_state["nro"] is not None:
                # Editar préstamo existente
                st.session_state["prestamos"].iloc[st.session_state["nro"]] = nuevo_prestamo
            else:
                # Crear un nuevo préstamo
                guardar_prestamo(nuevo_prestamo)

            save_data(st.session_state["prestamos"])  # Asegurar que se guarden los cambios
            st.success("Préstamo guardado con éxito.")
            st.session_state["page"] = "prestamo"
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
