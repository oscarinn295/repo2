import pandas as pd
import requests
import re
import streamlit as st
import login
from datetime import date
login.generarLogin()
# ID de la carpeta en Google Drive
DRIVE_FOLDER_ID = st.secrets['ids']['imagenes']
UPLOAD_URL = st.secrets['api']['imgs']

# Cargar datos
idc = st.secrets['ids']['cobranzas']
url = st.secrets['urls']['cobranzas']

def load():
    return login.load_data(url)

def save(df):
    login.save_data(idc, df)
    st.session_state['cobranzas'] = load()

def upload_to_drive(image_path, folder_id):
    with open(image_path, "rb") as image_file:
        files = {"image": (image_path, image_file, "image/jpeg")}
        data = {"folderId": folder_id}
        response = requests.post(UPLOAD_URL, files=files, data=data)

    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("url") if response_data.get("status") == "success" else None
    return None

def convert_drive_url(url):
    clean_url = url.split('?')[0]
    match = re.search(r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)', clean_url)
    
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    return url  # Retorna la URL original si no es un enlace válido de Drive


if 'page' not in st.session_state:
    st.session_state['page'] = 'main'
if 'cobranzas' not in st.session_state:
    st.session_state['cobranzas']=load()
    

def update_data(index, action, value=None):
    df = st.session_state["cobranzas"]
    if action == "estado":
        df.at[index, "estado"] = value
    elif action == "visita":
        df.at[index, "visita"] = value
    save(df)
if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1
def display_table(search_query=""):
    st.subheader("Cobranzas")
    df = st.session_state["cobranzas"]

    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
    # Configuración de paginación
    ITEMS_POR_PAGINA = 10
    # Paginación
    total_paginas = (len(df) // ITEMS_POR_PAGINA) + (1 if len(df) % ITEMS_POR_PAGINA > 0 else 0)
    inicio = (st.session_state['pagina_actual'] - 1) * ITEMS_POR_PAGINA
    fin = inicio + ITEMS_POR_PAGINA
    df_paginado = df.iloc[inicio:fin]
    if not df_paginado.empty:
        for idx, row in df_paginado.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f" **Vencimiento**:{row["vencimiento"].date()}")
                    st.write(f"**Cuota**: {row['n_cuota']} | **Monto**: {row['monto']}")
                    st.write(f"**Cliente**: {row['nombre']}")
                with col2:
                    option = st.selectbox("Acción", ["Seleccionar...", "Registrar pago", "Reprogramar visita", "No abono"], key=f"action_{idx}")
                    if option == "Registrar pago":
                        st.session_state['page'] = 'registrar'
                        st.session_state['dato'] = row.to_dict()
                        st.session_state['index'] = idx
                        st.rerun()
                with col3:
                    if pd.notna(row["comprobante"]):
                        image_url = convert_drive_url(row["comprobante"])
                        st.write("Comprobante:")
                        st.image(image_url, width=100)
                        st.markdown(f'[Descargar Comprobante]({image_url})', unsafe_allow_html=True)
    else:
        st.warning("No se encontraron resultados.")
    # Controles de paginación
    with st.container(border=True):
        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
        with col_pag1:
            if st.session_state['pagina_actual'] > 1:
                if st.button("⬅ Anterior"):
                    st.session_state['pagina_actual'] -= 1
                    st.rerun()
        with col_pag3:
            if st.session_state['pagina_actual'] < total_paginas:
                if st.button("Siguiente ➡"):
                    st.session_state['pagina_actual'] += 1
                    st.rerun()
    # Contador de registros y selector de cantidad por página
    with st.container(border=True):
        st.write(f"Se muestran de {inicio + 1} a {min(fin, len(df))} de {len(df)} resultados")
        items_seleccionados = st.selectbox("Por página", [10, 25, 50, 100], index=[10, 25, 50, 100].index(ITEMS_POR_PAGINA))
        if items_seleccionados != ITEMS_POR_PAGINA:
            ITEMS_POR_PAGINA = items_seleccionados
            st.session_state['pagina_actual'] = 1
            st.rerun()

if st.session_state["page"] == "main":
    st.title("Lista de Cobranzas")
    search_query = st.text_input("Buscar")
    display_table(search_query)
    if st.button('Ver todos los datos'):
        st.dataframe(load())

if st.session_state['page'] == 'registrar':
    with st.form("form_registro"):
        medio_pago = st.selectbox('Seleccione una opción', ['Seleccione una opción', 'efectivo', 'transferencia'])
        pago_total = st.checkbox(label='Pago Total')
        monto = st.number_input("Monto", min_value=0.0, step=1000.0, value=st.session_state['dato']['monto'] if pago_total else 0.0)
        comprobante = ""

        if medio_pago == 'transferencia':
            uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])
            if uploaded_file and st.button('Confirmar subida'):
                temp_path = f"./{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                comprobante = upload_to_drive(temp_path, DRIVE_FOLDER_ID)
                if comprobante:
                    st.success("Imagen subida correctamente")
                else:
                    st.error("Error al subir la imagen")

        registrar = st.form_submit_button("Registrar")
        volver = st.form_submit_button("Volver")

        if volver:
            st.session_state["page"] = 'main'
            st.rerun()

        if registrar:
            reg = st.session_state['dato']
            if medio_pago != 'Seleccione una opción' and monto > 0:
                actualizacion = {
                    'id': reg['id'],
                    'dni': reg['dni'],
                    'vendedor/cobrador': reg['vendedor/cobrador'],
                    'nombre': reg['nombre'],
                    'n_cuota': reg['n_cuota'],
                    'monto': reg['monto'],
                    'monto_mecalculado_mora': reg['monto_mecalculado_mora'],
                    'pago': monto,
                    'redondeo': 0.0,
                    'vencimiento': reg['vencimiento'],
                    'visita': reg['visita'],
                    'estado': 'Abonado',
                    'comprobante': comprobante
                }
                st.session_state['cobranzas'].loc[st.session_state['index']] = pd.Series(actualizacion)
                save(st.session_state['cobranzas'])
                st.session_state["page"] = 'main'
                st.rerun()
            else:
                st.warning('Faltan datos')
