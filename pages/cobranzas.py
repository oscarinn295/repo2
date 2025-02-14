
import pandas as pd
import requests
import re
import streamlit as st
import login
from datetime import date
if 'prestamos' not in st.session_state:
    st.session_state["prestamos"] = login.load_data(st.secrets['urls']['prestamos'])
st.session_state['cobranzas'] = login.load_data(st.secrets['urls']['cobranzas'])
login.generarLogin()


# Cargar datos
idc = st.secrets['ids']['cobranzas']
url = st.secrets['urls']['cobranzas']

def load():
    return login.load_data(url)

def save(id,column,data):#modifica un solo dato
    login.save_data(id,column,data,idc)

def delete(index):#borra una fila completa y acomoda el resto de la hoja para que no quede el espacio en blanco
    login.delete_data(index,st.secrets['ids']['cobranzas'])

def upload_to_drive(image_path, folder_id):
    pass

def convert_drive_url(url):
    pass




from datetime import datetime
import datetime as dt
prestamos=st.session_state["prestamos"]
import pandas as pd
from datetime import date
import numpy as np
# Definir función de recálculo
def calcular_recargo(cobranza):
    prestamo = prestamos[prestamos['id'] == cobranza['prestamo_id']]
    
    # Si el préstamo no existe, mantener los valores originales
    if pd.isna(cobranza['prestamo_id']) or prestamo.empty:
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']], 
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])

    vencimiento = prestamo['vence'].iloc[0]
    
    tipo_prestamo = {
        'Mensual: 1-10': 300,
        'Mensual: 10-20': 300,
        'Mensual: 20-30': 300,
        'Quincenal': 500,
        'Semanal: lunes': 400,
        'Semanal: martes': 400,
        'Semanal: miercoles': 400,
        'Semanal: jueves': 400,
        'Semanal: viernes': 400,
        'Semanal: sabado': 400,
        'indef': 0
    }
    
    hoy = pd.Timestamp(date.today())

    # Si no hay fecha de vencimiento, mantener valores originales
    if pd.isna(vencimiento):
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']], 
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])

    dias_mora = (hoy - pd.to_datetime(cobranza['vencimiento'])).days

    # Si la fecha es futura o el estado es "pago total", mantener los valores originales
    if dias_mora <= 0 or cobranza['estado'] == 'pago total':
        return pd.Series([cobranza['dias_mora'], cobranza['mora'], cobranza['monto_recalculado_mora']], 
                         index=['dias_mora', 'mora', 'monto_recalculado_mora'])

    # Si hay mora, calcular los intereses
    interes = tipo_prestamo.get(prestamo['vence'].iloc[0], 0)  # Asegurar que toma el tipo correcto
    interes_por_mora = interes * max(0, dias_mora)
    monto_recalculado_mora = cobranza['monto'] + interes_por_mora

    return pd.Series([dias_mora, interes_por_mora, monto_recalculado_mora], 
                     index=['dias_mora', 'mora', 'monto_recalculado_mora'])

col1,col2,col3,col4,col5,col6=st.columns(6)
with col6:
    if st.button('calcular regargos por mora'):
        cobranzas = load()
        # Aplicar la función correctamente y asignar los valores de vuelta
        cobranzas[['dias_mora', 'mora', 'monto_recalculado_mora']] = cobranzas.apply(calcular_recargo, axis=1)

        # Asegurar que las columnas estén en el orden correcto
        column_order = ['id',"vendedor", "nombre", "n_cuota", "monto", "vencimiento", 
            "dias_mora", "mora", "monto_recalculado_mora", "pago", "redondeo", 
            "estado", "comprobante", "prestamo_id", "cobrador", "fecha_cobro"
        ]
        cobranzas = cobranzas[column_order]

        # Reemplazar NaN y NaT en todas las columnas
        cobranzas = cobranzas.replace({np.nan: "", pd.NaT: ""})
        cobranzas.loc[pd.to_datetime(cobranzas['vencimiento']).dt.date>date.today(),'estado']='pendiente de pago'
        cobranzas['vencimiento'] = pd.to_datetime(cobranzas['vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y')
        # Solución específica para la columna 'fecha_cobro'
        cobranzas['fecha_cobro'] = pd.to_datetime(cobranzas['fecha_cobro'], errors='coerce').dt.strftime('%d-%m-%Y')
        cobranzas['fecha_cobro'] = cobranzas['fecha_cobro'].replace("NaT", "")
        cobranzas['fecha_cobro'] = cobranzas['fecha_cobro'].fillna("").astype(str)
        # Convertir a lista de listas para subir a Google Sheets
        data_to_upload = [cobranzas.columns.tolist()] + cobranzas.astype(str).values.tolist()
        # Sobrescribir en Google Sheets
        sheet_id = st.secrets['ids']['cobranzas']
        login.overwrite_sheet(data_to_upload, sheet_id)



def ingreso(cobranza,des):
    st.session_state["mov"]=login.load_data(st.secrets['urls']['flujo_caja'])
    caja=st.session_state["mov"]
    caja['saldo'] = pd.to_numeric(caja['saldo'], errors='coerce')
    mov=[date.today().strftime("%d-%m-%Y"),
        f"COBRANZA CUOTA NRO: {cobranza["n_cuota"]}, {des}",
        cobranza['pago'],
        0,
        cobranza['pago'],
        caja['saldo'].sum()+cobranza['pago']
        ]
    login.append_data(mov,st.secrets['ids']['flujo_caja'])
vendedores = st.session_state['usuarios']['usuario'].tolist()
def registrar(cobranza):
    import numpy as np
    pago=st.selectbox('monto',['pago',f'pago total: {cobranza['monto_recalculado_mora']}','otro monto'],index=0,key=f"pago{cobranza['id']}")
    if pago=='pago total':
        monto = cobranza['monto_recalculado_mora']
        registro='pago total'
    else:
        monto = st.number_input("Monto", min_value=0.0,max_value=float(cobranza['monto_recalculado_mora']), step=1000.0, key=f"monto_{cobranza['id']}")
        if monto<cobranza['monto_recalculado_mora']:
            registro='pago parcial'
        else:
            registro='pago total'
    medio_pago = st.selectbox('Seleccione una opción', ['Seleccione una opción', 'efectivo', 'transferencia'], key=f"medio_{cobranza['id']}")
    comprobante = ""

    if medio_pago == 'transferencia':
        pass
    with st.form(f"registrar_pago{cobranza['id']}"):
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
                ('estado', registro),
                ('comprobante', comprobante),
                ('fecha_cobro',date.today().strftime('%d-%m-%Y'))
            ]
            for col, dato in actualizacion:
                save(cobranza['id'], col, dato)
            if registro=='pago total' or monto==cobranza['monto']:
                save(cobranza['id'],'estado',registro)
                save(cobranza['id'], 'monto', float(cobranza['monto']) - monto)
            else:
                save(cobranza['id'], 'monto', float(cobranza['monto']) - monto)
            ingreso(cobranza, registro)
            st.session_state['cobranzas']=load()
            st.rerun()
        else:
            st.warning('Faltan datos')

def no_abono(cobranza):

    import numpy as np
    cobranza['vencimiento'] = str(cobranza['vencimiento'])
    cobranza = cobranza.replace({np.nan: ""}) 
    save(cobranza['id'],'estado','en mora')
    st.rerun()

if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1
st.session_state['cobranzas']['id'] = pd.to_numeric(st.session_state['cobranzas']['id'], errors='coerce').astype('Int64')


clientes=st.session_state['clientes']['nombre'].values.tolist()
def display_table():
    # Crear una copia del DataFrame original
    df = st.session_state["cobranzas"].copy()
    # Convertir 'vencimiento' a datetime para facilitar el filtrado
    df['vencimiento_dt'] = pd.to_datetime(df['vencimiento'], errors='coerce')
    col1,col2,col3,col4=st.columns(4)
    # Filtros en un expander
    with col4:
        with st.popover("Filtros"):
            reset = st.button("Resetear filtros")
            
            # Filtro de fecha opcional
            aplicar_fecha = st.checkbox("Filtrar por fecha", value=False)
            if aplicar_fecha:
                desde = st.date_input("Desde", value=date.today())
                hasta = st.date_input("Hasta", value=date.today())
            else:
                desde, hasta = None, None
            
            # Filtros de cliente y vendedor con opción "Todos"
            cliente = st.selectbox("Cliente", ["Todos"] + clientes, key='filtro1')
            vendedor = st.selectbox("Vendedor", ["Todos"] +vendedores, key='filtro2')

    # Si no se pulsa reset, aplicamos filtros acumulativos
    if not reset:
        if aplicar_fecha and desde and hasta:
            df = df[(df['vencimiento_dt'] >= pd.Timestamp(desde)) &
                    (df['vencimiento_dt'] <= pd.Timestamp(hasta))]
        if cliente != "Todos":
            df = df[df['nombre'] == cliente]
        # Para el filtro de vendedor:
        if st.session_state['user_data']['permisos'].iloc[0] == 'admin':
            if vendedor != "Todos":
                df = df[df['vendedor'] == vendedor]
        else:
            # Usuario no admin: filtrar siempre por su usuario
            df = df[df['vendedor'] == st.session_state['usuario']]
    else:
        # Si se pulsa reset, se recarga el DataFrame original
        df = st.session_state["cobranzas"].copy()

    # --- Paginación y despliegue del DataFrame filtrado ---
    ITEMS_POR_PAGINA = 10
    total_paginas = (len(df) // ITEMS_POR_PAGINA) + (1 if len(df) % ITEMS_POR_PAGINA > 0 else 0)
    inicio = (st.session_state['pagina_actual'] - 1) * ITEMS_POR_PAGINA
    fin = inicio + ITEMS_POR_PAGINA
    df_paginado = df.iloc[inicio:fin]
    
    if not df_paginado.empty:
        for idx, row in df_paginado.iterrows():
            with st.container():
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
                with col1:
                    st.write(f"**Vencimiento**: {row['vencimiento']}")
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
                        # Aquí podrías agregar la imagen o enlace del comprobante
                    else:
                        with st.popover('Actualizar'):
                            registrar(row)
    else:
        st.warning("No se encontraron resultados.")

    # --- Controles de paginación ---
    with st.container():
        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
        with col_pag1:
            if st.session_state['pagina_actual'] > 1:
                if st.button("⬅ Anterior"):
                    st.session_state['pagina_actual'] -= 1
                    st.experimental_rerun()
        with col_pag3:
            if st.session_state['pagina_actual'] < total_paginas:
                if st.button("Siguiente ➡"):
                    st.session_state['pagina_actual'] += 1
                    st.experimental_rerun()
    
    st.write(f"Se muestran de {inicio + 1} a {min(fin, len(df))} de {len(df)} resultados")

    items_seleccionados = st.selectbox("Por página", [10, 25, 50, 100], index=[10, 25, 50, 100].index(ITEMS_POR_PAGINA),key='paginado')
    if items_seleccionados != ITEMS_POR_PAGINA:
        ITEMS_POR_PAGINA = items_seleccionados
        st.session_state['pagina_actual'] = 1
        st.rerun()
    if not reset:
        with st.expander('datos filtrados'):
            st.subheader("Pendientes de pago")
            st.dataframe(df[df['estado'] == 'pendiente de pago'])

            st.subheader("En mora")
            st.dataframe(df[df['estado'] == 'en mora'])

            st.subheader("Pagados")
            st.dataframe(df[df['estado'] == 'pago total'])
st.title("Cobranzas")
display_table()
with st.expander('Ver todos los datos'):
    st.dataframe(load())