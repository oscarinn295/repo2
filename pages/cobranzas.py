
import pandas as pd
import requests
import re
import streamlit as st
import login
from datetime import date
if 'prestamos' not in st.session_state:
    st.session_state["prestamos"] = login.load_data(st.secrets['prueba_urls']['prestamos'])
if 'en_mora' not in st.session_state:
    st.session_state['en_mora'] = login.load_data(st.secrets['prueba_urls']['en_mora'])
if 'pendiente' not in st.session_state:
    st.session_state['pendiente'] = login.load_data(st.secrets['prueba_urls']['pendientes'])
if 'pagados' not in st.session_state:
    st.session_state['pagados'] = login.load_data(st.secrets['prueba_urls']['pagados'])
if 'cobranzas' not in st.session_state:
    st.session_state['cobranzas'] = login.load_data(st.secrets['prueba_urls']['cobranzas'])
login.generarLogin()
# ID de la carpeta en Google Drive
DRIVE_FOLDER_ID = st.secrets['ids']['imagenes']
UPLOAD_URL = st.secrets['api']['imgs']

# Cargar datos
idc = st.secrets['prueba_ids']['cobranzas']
url = st.secrets['prueba_urls']['cobranzas']

def load():
    return login.load_data(url)

def save(id,column,data):#modifica un solo dato
    login.save_data(id,column,data,idc)

def delete(index):#borra una fila completa y acomoda el resto de la hoja para que no quede el espacio en blanco
    login.delete_data(index,st.secrets['prueba_ids']['cobranzas'])

def upload_to_drive(image_path, folder_id):
    with open(image_path, "rb") as image_file:
        files = {"file": (image_path, image_file, "image/png")}
        data = {"folderId": folder_id}
        response = requests.post(UPLOAD_URL, files=files, data=data)

    response_data = response.json()
    return response_data.get("url") 

def convert_drive_url(url):
    clean_url = url.split('?')[0]
    match = re.search(r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)', clean_url)
    
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    return url  # Retorna la URL original si no es un enlace válido de Drive


cobranzas=st.session_state['cobranzas']
prestamos=st.session_state['prestamos']
from datetime import datetime
import datetime as dt
def calcular_recargo(df_cobranzas, df_prestamos):
    tipo_prestamo = {'mensual': 300, 'semanal': 400, 'quincenal': 500}
    hoy = pd.Timestamp(date.today())

    def calcular_fila(cobranza):
        if pd.isna(cobranza['prestamo_id']):
            return cobranza['monto']
        prestamo = df_prestamos[df_prestamos['id'] == cobranza['prestamo_id']]
        if prestamo.empty:
            return cobranza['monto']
        diff = (hoy - cobranza['vencimiento']).days
        return tipo_prestamo.get(prestamo.iloc[0]['tipo'], 0) * diff + cobranza['monto']

    df_cobranzas['monto_recalculado_mora'] = df_cobranzas.apply(calcular_fila, axis=1)
    return df_cobranzas

st.session_state['cobranzas'] = calcular_recargo(st.session_state['cobranzas'], st.session_state['prestamos'])

#for idx,cobranza in st.session_state['cobranzas'].iterrows():
#    save(cobranza['id'],'monto_recalculado_mora',recargo(cobranza))

def ingreso(cobranza,des):
    st.session_state["mov"]=login.load_data(st.secrets['prueba_urls']['flujo_caja'])
    caja=st.session_state["mov"]
    caja['saldo'] = pd.to_numeric(caja['saldo'], errors='coerce')
    mov=[date.today().strftime("%Y-%m-%d"),
        f"COBRANZA CUOTA NRO: {cobranza["n_cuota"]}, {des}",
        cobranza['pago'],
        0,
        cobranza['pago'],
        caja['saldo'].sum()+cobranza['pago']
        ]
    login.append_data(mov,st.secrets['prueba_ids']['flujo_caja'])

def registrar(cobranza):
    import numpy as np
    pago_total = st.checkbox(label='Pago Total', key=f"total_{cobranza['id']}")
    if pago_total:
            st.write(cobranza['monto_recalculado_mora'])
            monto = cobranza['monto_recalculado_mora']
    else:
        monto = st.number_input("Monto", min_value=0.0,max_value=float(cobranza['monto']), step=1000.0, key=f"monto_{cobranza['id']}")
    medio_pago = st.selectbox('Seleccione una opción', ['Seleccione una opción', 'efectivo', 'transferencia'], key=f"medio_{cobranza['id']}")
    comprobante = ""

    if medio_pago == 'transferencia':
        uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"], key=f"file_{cobranza['id']}")
        if uploaded_file and st.button('Confirmar subida'):
            temp_path = f"./{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            comprobante = upload_to_drive(temp_path, DRIVE_FOLDER_ID)
            if comprobante:
                st.success("Imagen subida correctamente")
            else:
                    st.error("Error al subir la imagen")
    with st.form(f"registrar_pago{cobranza['id']}"):
        vendedores = login.load_data1(st.secrets['prueba_urls']['usuarios'])['usuario'].values.tolist()
        cobrador = st.selectbox('Cobrador', vendedores, key=f"cobradores_{cobranza['id']}")
        submit_button = st.form_submit_button("Registrar")

    if submit_button:
        cobranza['vencimiento'] = str(cobranza['vencimiento'])
        cobranza = cobranza.replace({np.nan: ""})
        if medio_pago != 'Seleccione una opción' and monto > 0:
            actualizacion = [
                ('cobrador', cobrador),
                ('pago', cobranza['pago']+monto),
                ('redondeo', 0.0),
                ('estado', 'Abonado' if pago_total else 'Pagado parcialmente'),
                ('comprobante', comprobante)
            ]
            for col, dato in actualizacion:
                save(cobranza['id'], col, dato)
            if pago_total or monto==cobranza['monto']:
                save(cobranza['id'],'estado','Pagado Completo')
                save(cobranza['id'], 'monto', float(cobranza['monto']) - monto)
            else:
                save(cobranza['id'], 'monto', float(cobranza['monto']) - monto)
            login.append_data(cobranza.values.tolist(), st.secrets['prueba_ids']['pagados'])
            st.session_state['pagados']=login.load_data(st.secrets['prueba_urls']['pagados'])
            ingreso(cobranza, 'total' if (pago_total or monto==cobranza['monto']) else 'parcial')
            st.session_state['cobranzas']=load()
            st.rerun()
        else:
            st.warning('Faltan datos')

def no_abono(cobranza):

    import numpy as np
    cobranza['vencimiento'] = str(cobranza['vencimiento'])
    cobranza = cobranza.replace({np.nan: ""}) 
    save(cobranza['id'],'estado','no abono')
    login.append_data(cobranza.values.tolist(),st.secrets['prueba_ids']['en_mora'])
    st.session_state['cobranzas']=load()
    st.session_state['en_mora']=login.load_data(st.secrets['prueba_urls']['en_mora'])
    st.rerun()

if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1
st.session_state['cobranzas']['id'] = pd.to_numeric(st.session_state['cobranzas']['id'], errors='coerce').astype('Int64')
def display_table(search_query=""):
    st.subheader("Cobranzas")
    df = st.session_state["cobranzas"]

    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
    if st.session_state['user_data']['permisos'].iloc[0]!='admin':
        df=df[df['vendedor']==st.session_state['usuario']]
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
                col1, col2, col3,col4,col5,col6,col7,col8 = st.columns(8)
                with col1:
                    st.write(f" **Vencimiento**: {row["vencimiento"].date()}")
                with col2:
                    st.write(f"Vendedor: {row['vendedor']}")
                    st.write(f"**Cliente**: {row['nombre']}")
                with col3:
                    st.write(f"**Cuota**: {row['n_cuota']}... **Monto**: {row['monto']}")
                with col4:
                    st.write(f"Monto Recalculado (+Mora): {row['monto_recalculado_mora']}")                    
                with col5:
                    st.write(f"Monto Pago: {row['pago']}")        
                with col6:
                    st.write(f"Redondeo: {row['redondeo']}")
                with col7:
                    st.write(f"{row['estado']}")
                with col8:
                    if pd.notna(row["comprobante"]):
                        st.write(f"{row['comprobante']}")
                        #image_url = convert_drive_url(row["comprobante"])
                        #st.write("Comprobante:")
                        #st.image(image_url, width=100)
                        #st.markdown(f'[Descargar Comprobante]({image_url})', unsafe_allow_html=True)
                    else:
                        with st.expander('actualizar'):
                            with st.popover("Registrar pago"):
                                registrar(row)
                            if st.button("No abono",key=f"no_{row['id']}"):
                                no_abono(row)

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
        items_seleccionados = st.selectbox("Por página", [10, 25, 50, 100], index=[10, 25, 50, 100].index(ITEMS_POR_PAGINA),key='paginado')
        if items_seleccionados != ITEMS_POR_PAGINA:
            ITEMS_POR_PAGINA = items_seleccionados
            st.session_state['pagina_actual'] = 1
            st.rerun()


st.title("Cobranzas")
querys=[]
col1,col2,col3=st.columns(3)
with col3:
    with st.popover('Filtros'):
        col1,col2=st.columns(2)
        with col1:
            st.write('Filtros')
        with col2:
            reset=st.button('Resetear los filtros')
        desde=st.date_input('Desde')
        hasta=st.date_input('Hasta')
        vendedor=st.selectbox('Vendedor',[],key='filtro1')
        tipo_pago=st.selectbox('Tipo Pago',[],key='filtro2')
        condicion='preparar condicion'
        if condicion:
            querys.append([desde, hasta,vendedor,tipo_pago])
        if reset:
                querys=[]
display_table()
st.dataframe(st.session_state['en_mora'])
st.dataframe(st.session_state['pagados'])
with st.expander('Ver todos los datos'):
    st.dataframe(load())