import login
import pandas as pd
import streamlit as st
from datetime import date

# Iniciar sesión
login.generarLogin()

# Cargar datos desde secretos
try:
    ID_VISITAS = st.secrets['ids']['visitas']
    url = st.secrets['urls']['visitas']
    url_clientes = st.secrets['urls']['clientes']
except KeyError:
    st.error("Error: No se encontraron claves en los secretos de Streamlit.")
    st.stop()

# Funciones de carga y guardado de datos
def load():
    data = login.load_data(url)
    if not isinstance(data, pd.DataFrame) or data.empty:
        st.warning("Advertencia: No se pudieron cargar las visitas.")
        return pd.DataFrame(columns=["nro", "visita", "vendedor", "nombre", "fecha", "notas"])
    return data

def save(df):
    login.save_data(ID_VISITAS, df)
    st.session_state['visitas'] = load()

def new(datos):
    login.append_data(ID_VISITAS, datos)
    st.session_state['visitas'] = load()

# Inicialización de session_state
time_session = ['page', 'visitas', 'nro', 'usuario']
for key in time_session:
    if key not in st.session_state:
        st.session_state[key] = 'visitas' if key == 'page' else None

# Verificar usuario antes de continuar
if not st.session_state['usuario']:
    st.error("Error: No hay usuario en la sesión.")
    st.stop()

# Cargar visitas
if 'visitas' not in st.session_state or not isinstance(st.session_state['visitas'], pd.DataFrame):
    st.session_state['visitas'] = load()

# Cargar clientes
clientes = login.load_data(url_clientes)
if not isinstance(clientes, pd.DataFrame) or clientes.empty:
    st.warning("Advertencia: No se pudieron cargar los clientes.")
    clientes = pd.DataFrame(columns=["nombre"])

# Función para mostrar la tabla con filtro
def display_table(search_query=""):
    st.subheader("Cobranzas")
    df = st.session_state["visitas"]

    if df.empty:
        st.warning("No hay visitas registradas.")
        return

    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]

    for idx, row in df.iterrows():
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.write(f"**Visita**: {row['visita']} | **Vendedor**: {row['vendedor']}")
            st.write(f"**Cliente**: {row['nombre']} | **Fecha Visita**: {row['fecha']}")
            st.write(f"**Notas**: {row['notas']}")
        with col2:
            if st.button(f'Editar', key=f'edit_{idx}'):
                st.session_state['nro'] = idx
                st.session_state['page'] = 'reg'
                st.rerun()
        with col3:
            if st.button(f'Borrar', key=f'del_{idx}'):
                st.session_state["visitas"] = st.session_state["visitas"].drop(idx).reset_index(drop=True)
                save(st.session_state["visitas"])
                st.rerun()

# Página de registro
def registrar_visita():
    lista_clientes = clientes['nombre'].tolist()
    nro = st.session_state.get("nro")
    visita = st.session_state["visitas"].loc[nro] if nro in st.session_state["visitas"].index else None
    
    st.title("Crear Visita Registrada")
    with st.form("visita"):
        tipo = st.selectbox('Seleccione una opción', ['Cobranza', 'Reprogramacion', 'No Abono'],
                            index=['Cobranza', 'Reprogramacion', 'No Abono'].index(visita['visita']) if visita else 0)
        vendedor = visita['vendedor'] if visita else st.session_state['usuario']
        nombre_cliente = st.selectbox('Cliente', lista_clientes,
                                      index=lista_clientes.index(visita['nombre']) if visita and visita['nombre'] in lista_clientes else 0)
        fecha = st.date_input("Fecha", value=visita['fecha'] if visita is not None else date.today())
        notas = st.text_area("Notas", value=visita['notas'] if visita is not None else "")
        submit_button = st.form_submit_button("Guardar")
    
    if submit_button:
        if visita is None:
            nuevo_cliente = pd.DataFrame([{ "nro": len(st.session_state["visitas"]) + 1, "visita": tipo, "vendedor": vendedor,
                                            "nombre": nombre_cliente, "fecha": fecha, "notas": notas }])
            st.session_state["visitas"] = pd.concat([st.session_state["visitas"], nuevo_cliente], ignore_index=True)
        else:
            st.session_state["visitas"].loc[nro, ["visita", "vendedor", "nombre", "fecha", "notas"]] = [tipo, vendedor, nombre_cliente, fecha, notas]
        save(st.session_state["visitas"])
        st.session_state['page'] = 'visitas'
        st.rerun()

    if st.button("Volver"):
        st.session_state['page'] = 'visitas'
        st.rerun()

# Página de carga de archivos CSV
if st.session_state['usuario'] == "admin":
    st.title("Subir nuevos datos")
    uploaded_file = st.file_uploader("Sube un archivo CSV", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("Archivo cargado con éxito!")
        st.subheader("Vista previa de los datos:")
        st.dataframe(df.head())
        st.subheader("Descripción estadística:")
        st.write(df.describe())
        st.subheader("Columnas del archivo:")
        st.write(df.columns.tolist())
    else:
        st.info("Por favor, sube un archivo para comenzar.")

# Controlador de páginas
if st.session_state['page'] == 'visitas':
    st.title("Visitas")
    if st.button('Crear Visita Registrada'):
        st.session_state['page'] = 'reg'
        st.rerun()
    display_table()
elif st.session_state['page'] == 'reg':
    registrar_visita()
