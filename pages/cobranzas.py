import os
import pandas as pd
import streamlit as st
import login

login.generarLogin()

# Ruta de los archivos
FILE_PATH = "C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\DB\\cobranzas.xlsx"
CLIENTS_PATH = "C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\DB\\clientes.xlsx"

# Cargar clientes
clientes = pd.read_excel(CLIENTS_PATH, engine="openpyxl")

# Función para cargar datos de cobranzas
def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_excel(FILE_PATH, engine="openpyxl")
    else:
        return pd.DataFrame(columns=[
            "ID", "DNI", "Vendedor/Cobrador", "nombre", "N° Cuota",
            "monto", "Monto Recalculado (+ Mora)", "pago", "redondeo",
            "vencimiento", "visita", "estado"
        ])

# Función para guardar datos
def save_data(dataframe):
    dataframe.to_excel(FILE_PATH, index=False, engine="openpyxl")
    st.session_state["cobranzas"] = dataframe

# Inicializar archivo si no existe
if "cobranzas" not in st.session_state:
    st.session_state["cobranzas"] = load_data()

st.session_state['pages']='cobranza'
# Función para actualizar datos
def update_data(index, action, value=None):
    df = st.session_state["cobranzas"]
    if action == "estado":
        df.at[index, "estado"] = value
    elif action == "visita":
        df.at[index, "visita"] = value
    save_data(df)

# Función para crear cobranzas
def crear_cobranzas(data):
    for i in range(1, data["Cant. Cuotas"] + 1):
        nueva_cobranza = {
            "ID": st.session_state["cobranzas"]["ID"].max() + 1 if not st.session_state["cobranzas"].empty else 1,
            "DNI": clientes.loc[clientes["nombre"] == data["nombre"], "dni"].values[0],
            "Vendedor/Cobrador": st.session_state["usuario"],
            "nombre": data["nombre"],
            "N° Cuota": i,
            "monto": data["monto"],
            "Monto Recalculado (+ Mora)": data["monto"],
            "pago": 0,  # Inicialmente no pagado
            "redondeo": 0,
            "vencimiento": data["vence dia"],
            "visita": data["fecha"],
            "estado": "Pendiente"
        }
        nueva_cobranza_df = pd.DataFrame([nueva_cobranza])
        st.session_state["cobranzas"] = pd.concat([st.session_state["cobranzas"], nueva_cobranza_df], ignore_index=True)
    save_data(st.session_state["cobranzas"])

# Mostrar tabla interactiva
def display_table(search_query=""):
    st.subheader("Cobranzas")
    df = st.session_state["cobranzas"]

    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]

    if not df.empty:
        for idx, row in df.iterrows():
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.write(f"**ID**: {row['ID']} | **Nombre**: {row['nombre']}")
                st.write(f"**Cuota**: {row['N° Cuota']} | **Monto**: {row['monto']}")
                st.write(f"**Vencimiento**: {row['vencimiento']} | **Visita**: {row['visita']} | **Estado**: {row['estado']}")
            with col2:
                option = st.selectbox(
                    "Acción",
                    ["Seleccionar...", "Registrar pago", "Reprogramar visita", "No abono"],
                    key=f"action_{idx}"
                )
                if option == "Registrar pago":
                    new_state = st.text_input(f"Nuevo estado (ID {row['ID']})", key=f"state_{idx}")
                    if st.button("Actualizar estado", key=f"update_state_{idx}"):
                        update_data(idx, "estado", new_state)
                        st.success("Estado actualizado.")
                elif option == "Reprogramar visita":
                    new_visit = st.text_input(f"Nueva visita (ID {row['ID']})", key=f"visit_{idx}")
                    if st.button("Actualizar visita", key=f"update_visit_{idx}"):
                        update_data(idx, "visita", new_visit)
                        st.success("Visita actualizada.")
                elif option == "No abono":
                    if st.button("Marcar como No abono", key=f"no_abono_{idx}"):
                        update_data(idx, "estado", "No abono")
                        st.success("Estado actualizado a 'No abono'.")
    else:
        st.warning("No se encontraron resultados.")

# Página principal
if st.session_state["page"] == "cobranza":
    st.title("Lista de Cobranzas")
    search_query = st.text_input("Buscar")
    display_table(search_query)
