
import pandas as pd
import requests
import re
import streamlit as st
import login
from datetime import date
import meta_ediciones


if 'prestamos' not in st.session_state:
    st.session_state["prestamos"] = login.load_data(st.secrets['urls']['prestamos'])
if 'cobranzas' not in st.session_state:
    st.session_state['cobranzas'] = login.load_data(st.secrets['urls']['cobranzas'])
prestamos=st.session_state["prestamos"]
if st.session_state['user_data']['permisos'].iloc[0]!='admin':
    st.session_state["prestamos"]=st.session_state["prestamos"][st.session_state["prestamos"]['vendedor']==st.session_state['usuario']]
    st.session_state['cobranzas']=st.session_state['cobranzas'][st.session_state['cobranzas']['vendedor']==st.session_state['usuario']]
    prestamos=prestamos[prestamos['vendedor']==st.session_state['usuario']]
login.generarLogin()


# Cargar datos
idc = st.secrets['ids']['cobranzas']
url = st.secrets['urls']['cobranzas']

def load():
    df=login.load_data(url)
    if st.session_state['user_data']['permisos'].iloc[0]!='admin':
        df=df[df['vendedor']==st.session_state['usuario']]
    return df

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

import pandas as pd
from datetime import date
import numpy as np

cobranzas = load()
col1,col2,col3,col4,col5,col6=st.columns(6)
with col6:
    if st.button('reordenar datos'):
        # Aplicar ordenamiento
        df_cobranzas = meta_ediciones.ordenar_cobranzas(cobranzas)

        # Limpiar NaN y asegurar que los datos sean cadenas (Google Sheets espera texto en JSON)
        df_cobranzas = df_cobranzas.fillna("").astype(str)

        # Convertir DataFrame a lista de listas (incluyendo encabezados)
        data_to_save = [df_cobranzas.columns.tolist()] + df_cobranzas.values.tolist()

        # Verificar que haya datos antes de sobrescribir
        if len(data_to_save) > 1:
            login.overwrite_sheet(data_to_save, st.secrets['ids']['cobranzas'])
            st.success("✅ Datos actualizados correctamente en Google Sheets.")
        else:
            st.error("❌ Error: No hay datos válidos para guardar en Google Sheets.")
        st.rerun()

        
    if st.button('calcular regargos por mora'):
        # Aplicar la función correctamente y asignar los valores de vuelta
        cobranzas[['dias_mora', 'mora', 'monto_recalculado_mora']] = cobranzas.apply(meta_ediciones.calcular_recargo, axis=1)

        # Asegurar que las columnas estén en el orden correcto
        column_order = ['id','prestamo_id','entregado','tnm','cantidad de cuotas',
                        "vendedor", "nombre", "n_cuota", "monto", "vencimiento", 
                        "dias_mora", "mora",'capital','cuota pura','intereses',
                        'amortizacion','iva','monto_recalculado_mora','pago',
                        'redondeo','estado','medio de pago','cobrador','fecha_cobro' ]
        cobranzas = cobranzas[column_order]

        # Reemplazar NaN y NaT en todas las columnas
        cobranzas = cobranzas.replace({np.nan: "", pd.NaT: ""})
        cobranzas.loc[pd.to_datetime(cobranzas['vencimiento']).dt.date>date.today(),'estado']='Pendiente de pago'
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

def ingreso(cobranza,descripcion):
    st.session_state["mov"]=login.load_data(st.secrets['urls']['flujo_caja'])
    caja=st.session_state["mov"]
    caja['saldo'] = pd.to_numeric(caja['saldo'], errors='coerce')
    mov=[date.today().strftime("%d-%m-%Y"),
        f"COBRANZA CUOTA NRO: {cobranza["n_cuota"]}, {descripcion}",
        cobranza['pago'],
        0,
        cobranza['pago'],
        caja['saldo'].sum()+cobranza['pago']
        ]
    login.append_data(mov,st.secrets['ids']['flujo_caja'])
vendedores = st.session_state['usuarios']['usuario'].tolist()
import numpy as np
from datetime import date

def registrar(cobranza):

    fecha_cobro=st.selectbox(
        'fecha de cobro',
        ['seleccionar fecha','hoy','otra fecha'],
        index=0,key=f"vencimientoo{cobranza['id']}"
    )
    if 'hoy' in fecha_cobro:
        fecha_cobro=date.today().strftime("%d-%m-%Y")
    elif 'otra fecha':
        fecha_cobro=st.date_input('fecha del cobro',key=f"cobro{cobranza['id']}")
        fecha_cobro=fecha_cobro.strftime("%d-%m-%Y")
    pago = st.selectbox(
        'Monto',
        ['pago', f"Pago total: {cobranza['monto_recalculado_mora']}", 'otro monto'],
        index=0,
        key=f"pago{cobranza['id']}"
    )

    if 'Pago total' in pago:
        monto = cobranza['monto_recalculado_mora']
        registro = 'Pago total'
        st.write(f'monto a pagar: {monto}')
    elif 'otro monto' in pago:
        monto = st.number_input(
            "Monto",
            min_value=0.0,
            max_value=float(cobranza['monto_recalculado_mora']),
            value=0.0,
            step=1000.0,
            key=f"monto_{cobranza['id']}"
        )
        registro = 'Pago parcial' if monto < cobranza['monto_recalculado_mora'] else 'Pago total'

    medio_pago = st.selectbox(
        'Medio de pago', 
        ['Seleccione una opción', 'efectivo', 'transferencia','mixto'], 
        key=f"medio_{cobranza['id']}"
    )

    if medio_pago == 'transferencia':
        comprobante = st.text_input('Número de comprobante', key=f"comprobante_{cobranza['id']}")
    else:
        comprobante = ""

    with st.form(f"registrar_pago{cobranza['id']}"):
        cobrador = st.selectbox('Cobrador', vendedores, key=f"cobradores_{cobranza['id']}")
        obs=st.text_input('Observación',key=f'observacion_{cobranza['id']}')
        submit_button = st.form_submit_button("Registrar")
    if submit_button:
        if medio_pago == 'Seleccione una opción' or monto <= 0:
            st.warning('Faltan datos')
            return

        cobranza['vencimiento'] = str(cobranza['vencimiento'])
        cobranza = cobranza.replace({np.nan: 0})
        monto=float(monto)
        actualizacion = [
            ('cobrador', cobrador),
            ('pago', float(cobranza.get('pago', 0)) + monto),
            ('redondeo', 0.0),
            ('estado', registro),
            ('medio de pago',medio_pago),
            ('comprobante', comprobante),
            ('fecha_cobro', date.today().strftime('%d-%m-%Y')),
            ('monto', max(0, float(cobranza['monto']) - monto)),
            ('obs',obs)
        ]

        for col, dato in actualizacion:
            save(cobranza['id'], col, dato)

        ingreso(cobranza, registro)
        st.session_state['cobranzas'] = load()
        #login.historial()
        st.rerun()

def registrar_moroso(cobranza):
    morosos=login.load_data(st.secrets['urls']['repo_morosos'])
    int(st.session_state['cobranzas']['id'].max())
    moroso=[
            int(morosos['id'].max()),
            cobranza['nombre'],
            st.session_state['clientes'][st.session_state['clientes']['nombre']==cobranza['nombre']]['dni'],
            cobranza['n_cuota'],
            cobranza['monto'],
            cobranza['monto_recalculado_mora'],
            cobranza['dias_mora'],
            cobranza['mora']
        ]
    login.append_data(moroso,st.secrets['ids']['repo_morosos'])

def no_abono(cobranza):
    import numpy as np
    with st.form(f'no abono{cobranza['id']}'):
        st.text_input('obs',key=f"no abono_{cobranza['id']}")
        submit_button=st.form_submit_button('registrar')
    if submit_button:
        cobranza['vencimiento'] = str(cobranza['vencimiento'])
        cobranza = cobranza.replace({np.nan: ""}) 
        save(cobranza['id'],'estado','En mora')
        st.session_state['cobranzas']=load()

if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1
st.session_state['cobranzas']['id'] = pd.to_numeric(st.session_state['cobranzas']['id'], errors='coerce').astype('Int64')


clientes=st.session_state['clientes']['nombre'].values.tolist()
estados=['Pendiente de pago','En mora','Pago total','Pago parcial']
def display_table():
    # Crear una copia del DataFrame original
    df = st.session_state["cobranzas"].copy()
    df['vencimiento_dt'] = pd.to_datetime(df['vencimiento'], errors='coerce')
    
    col1, col2, col3, col4 = st.columns(4)

    with col4:
        with st.popover("Filtros"):
            reset = st.button("Resetear filtros")

            aplicar_fecha = st.checkbox("Filtrar por fecha", value=False)
            if aplicar_fecha:
                desde = st.date_input("Desde", value=date.today())
                hasta = st.date_input("Hasta", value=date.today())
            else:
                desde, hasta = None, None
            
            cliente = st.selectbox("Cliente", ["Todos"] + clientes, key='filtro1')
            vendedor = st.selectbox("Vendedor", ["Todos"] + vendedores, key='filtro2')
            estado = st.selectbox("Estado", ["Todos"] + estados, key='filtro3')

    if not reset:
        if aplicar_fecha and desde and hasta:
            df = df[(df['vencimiento_dt'] >= pd.Timestamp(desde)) & 
                    (df['vencimiento_dt'] <= pd.Timestamp(hasta))]
        if cliente != "Todos":
            df = df[df['nombre'] == cliente]
        if estado != "Todos":
            df = df[df['estado'] == estado]
        if st.session_state['user_data']['permisos'].iloc[0] == 'admin':
            if vendedor != "Todos":
                df = df[df['vendedor'] == vendedor]
        else:
            df = df[df['vendedor'] == st.session_state['usuario']]
    else:
        df = st.session_state["cobranzas"].copy()

    ITEMS_POR_PAGINA = 10
    total_paginas = (len(df) // ITEMS_POR_PAGINA) + (1 if len(df) % ITEMS_POR_PAGINA > 0 else 0)
    inicio = (st.session_state['pagina_actual'] - 1) * ITEMS_POR_PAGINA
    fin = inicio + ITEMS_POR_PAGINA
    df_paginado = df.iloc[inicio:fin]

    if not df_paginado.empty:
        for idx, row in df_paginado.iterrows():
            with st.container(border=True):
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

                with col1:
                    st.write(f"**Vencimiento**:")
                    st.write(f"{row['vencimiento']}")
                
                with col2:
                    st.write(f"**Vendedor**: {row['vendedor']}")
                    st.write(f"**Cliente**: \n",unsafe_allow_html=True)
                    st.write(f"{row['nombre']}")

                with col3:
                    st.write(f"**Cuota**: {row['n_cuota']}")
                    st.write(f"**Monto**: ${float(row['monto']):,.2f}")

                with col4:
                    st.write(f"**Amortización**: ${float(row['amortizacion']):,.2f}")
                    st.write(f"**Intereses**: ${float(row['intereses']):,.2f}")
                    st.write(f"**IVA**: ${float(row['iva']):,.2f}")

                with col5:
                    st.write(f"**Monto a pagar**: ${row['monto_recalculado_mora']:,.2f}")

                with col6:
                    if not pd.isna(row['pago']):
                        st.write(f"**Monto Pago**: ${float(row['pago']):,.2f}")
                        st.write(f"**Redondeo**: ${float(row['redondeo']):,.2f}")

                with col7:
                    st.write(f"**Estado**: \n", unsafe_allow_html=True)
                    st.write(f"{row['estado']}")

                with col8:
                    with st.expander('Actualizar: '):
                        with st.popover('Registrar pago'):
                            registrar(row)
                        with st.popover('No abonó'):
                            no_abono(row)
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
            st.dataframe(df[df['estado'] == 'Pendiente de pago'])

            st.subheader("En mora")
            st.dataframe(df[df['estado'] == 'En mora'])

            st.subheader("Pagados")
            st.dataframe(df[df['estado'] == 'Pago total'])
            st.subheader("Pagos parciales")
            st.dataframe(df[df['estado'] == 'Pago parcial'])
            st.subheader('Pendientes de actualizacion: ')
            # Convertir la columna 'vencimiento' a tipo datetime
            df['vencimiento'] = pd.to_datetime(df['vencimiento'], format='%d-%m-%Y')
            # Filtrar los registros vencidos con estado 'Pendiente de pago'
            df_vencidos = df[(df['vencimiento'] < pd.Timestamp.today()) & (df['estado'] == 'Pendiente de pago')]
            st.dataframe(df_vencidos)
st.title("Cobranzas")
display_table()
with st.expander('Ver todos los datos'):
    st.dataframe(load())