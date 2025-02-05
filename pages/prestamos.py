import streamlit as st
import login
from datetime import datetime
import datetime as dt
from dateutil.relativedelta import relativedelta
#gestionar prestamos, funciones
def generar_fechas_prestamos(fecha_registro:str, frecuencia:str, cuotas:int,vencimiento=None):
    """
    Genera fechas de pago a partir de las condiciones dadas.
    :param fecha_registro: que originalmente es un datetime pero como que no me estaba dejando guardar datetime
        así que primero son los strings que salen de eso
        los string de fecha para este caso tienen que venir con este formato %d/%m/%Y
    :param frecuencia: Frecuencia de pago ('semanal', 'quincenal', 'mensual')
    :param cuotas: Número de cuotas
    :vencimiento:10, 20 o 30
    :return: Lista de fechas de pago (list of datetime.date)
    """
    fecha_registro=datetime.strptime(fecha_registro, "%Y-%m-%d")
    fecha_actual=fecha_registro
    fechas=[]
    if frecuencia=='mensual':
        if vencimiento is not None:
            if int(fecha_registro.dt.day())<vencimiento:
                fecha_objetivo=fecha_registro+ dt.timedelta(days=vencimiento-fecha_registro.dt.day())
            elif int(fecha_registro.dt.day())>vencimiento:
                fecha_objetivo=fecha_registro+relativedelta(months=1)- dt.timedelta(days=fecha_registro.dt.day()-vencimiento)
        else:
            fecha_objetivo=fecha_registro+relativedelta(months=1)
        for _ in range(cuotas):
            fechas.append(fecha_objetivo.strftime("%Y-%m-%d"))
            fecha_objetivo+=relativedelta(months=1)
    elif frecuencia=='quincenal':
        for _ in range(cuotas):
            fecha_actual+=dt.timedelta(weeks=2)
            fechas.append(fecha_actual.strftime("%Y-%m-%d"))
    elif frecuencia=='semanal':
        for _ in range(int(cuotas)):
            fecha_actual+=dt.timedelta(weeks=1)
            fechas.append(fecha_actual.strftime("%Y-%m-%d"))
    return fechas

def crear_cobranzas(data,vencimiento=None):
    st.session_state['cobranzas']=login.load_data(st.secrets['urls']['cobranzas'])
    fechas=generar_fechas_prestamos(data[1],data[5], data[3],vencimiento)
    i=0
    for fecha in fechas:
        nueva_cobranza=[
            int(st.session_state['cobranzas']['id'].max()+1)+i,
            st.session_state['usuario'],
            data[2],
            int(i),
            float(data[10]),
            float(data[10]),
            0.0,
            0.0,
            fecha,
            'Pendiente de Pago'
            ]
        i+=1
        login.append_data(nueva_cobranza,st.secrets['ids']['cobranzas'])


from datetime import date
from dateutil.relativedelta import relativedelta

idc=st.secrets['ids']['prestamos']
url=st.secrets['urls']['prestamos']
clientes=login.load_data(st.secrets['urls']['clientes'])

def load():
    return login.load_data(url)
def new(datos):
    login.append_data(datos,idc)
    st.session_state['prestamos']=load()
def save(df):
    login.save_data(idc,df)
    st.session_state['prestamos']=load()

import pandas as pd

login.generarLogin()

from datetime import date
if 'page' not in st.session_state:
    st.session_state["page"] = "main"  # Página por defecto
if 'prestamos' not in st.session_state:
    st.session_state['prestamos']=load()
if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1





def egreso_caja(data):
    st.session_state["mov"]=login.load_data(st.secrets['urls']['flujo_caja'])
    caja=st.session_state["mov"]
    caja['saldo'] = pd.to_numeric(caja['saldo'], errors='coerce')
    mov=[
        data[1],
        f"PLAN {data[3]} CUOTAS DE {data[4]}",
        0,
        data[4],
        -data[4],
        caja['saldo'].sum()-data[4]
        ]
    login.append_data(mov,st.secrets['ids']['flujo_caja'])


def reporte_venta(data):
    venta=[
        str(st.session_state['usuario']),
        str(data[2]),
        int(data[0]),
        int(data[3]),
        float(data[4])
        ]
    login.append_data(venta,st.secrets['ids']['repo_ventas'])

vendedores=login.load_data1(st.secrets['urls']['usuarios'])['usuario'].values.tolist()

def crear():
    fecha =  date.today()
    col1, col2 = st.columns(2)
    lista=['seleccione un cliente']
    for nombre in clientes['nombre']:
        lista.append(nombre)
    with col1:
        nombre_cliente = st.selectbox('Cliente',lista)
        venc_dia=st.selectbox('Dia Vencimiento Cuota',["Seleccione una opción",'lunes','martes','miercoles','jueves','viernes','sabado'],key='dia')
        producto_asociado=st.text_input('Producto Asociado*',key='producto')
        estado = st.selectbox(
            "Estado*",
            ["Seleccione una opción",
            "pendiente",
            "aceptado",
            "liquidado",
            "al dia",
            "en mora",
            "en juicio",
            "cancelado",
            "finalizado"
            ],key='estadoo')
        tipo_prestamo = st.radio(
            "Tipo de Préstamo*",
            ["mensual",
            "quincenal",
            "semanal"],key='tipo')
    with col2:
        cantidad_cuotas = st.number_input("Cantidad de Cuotas*",
                                            min_value=1,
                                            step=1,key='cant')
        capital = st.number_input("Capital*", min_value=0.0, step=1000.0,key='capital')
        TNM=st.number_input('T.N.M*', min_value=0.0, step=0.1,key='tnm')
        monto=st.number_input('Monto Cuota',min_value=0.0, step=1000.0,key='monto')
        vendedor=st.selectbox('vendedor',vendedores)
    obs=st.text_input('Observaciones',key='obss')
    # Botón de acción dentro del formulario

    if st.button('crear',key='crearr'):
        nuevo_prestamo = [
            max(st.session_state['prestamos']['nro'],default=0) + 1,
            str(fecha),
            nombre_cliente,
            vendedor,
            cantidad_cuotas,
            capital,
            tipo_prestamo,
            estado,
            venc_dia,
            producto_asociado,
            TNM,
            monto,
            obs]
        new(nuevo_prestamo)
        egreso_caja(nuevo_prestamo)
        reporte_venta(nuevo_prestamo)
        crear_cobranzas(nuevo_prestamo)


def editar(prestamo):    # Si estamos editando un préstamo, cargar datos existentes
    st.subheader("Editar Prestamo")
    fecha = pd.to_datetime(prestamo["fecha"]).date() if prestamo["fecha"] else date.today()
    nombre_cliente = prestamo["nombre"]
    capital = prestamo["capital"]
    tipo_prestamo = prestamo["tipo"]
    cantidad_cuotas = prestamo["cantidad"]
    estado = prestamo["estado"]
    producto_asociado=prestamo["asociado"]
    TNM=prestamo['tnm']
    monto=prestamo["monto"]
    vence_dia=prestamo['vence dia']
    obs=prestamo["obs"]
    col1, col2 = st.columns(2)
    with col1:
        st.write(f'{prestamo['nombre']}')
        venc_dia=st.selectbox('Dia Vencimiento Cuota',["Seleccione una opción",'lunes','martes','miercoles','jueves','viernes','sabado'],
                            index=["Seleccione una opción",'lunes','martes','miercoles','jueves','viernes','sabado'].index(vence_dia),
                            key=f'diaa{prestamo['nro']}')
        producto_asociado=st.text_input('Producto Asociado*',value=producto_asociado,key=f'producto_{prestamo['nro']}')
        estado = st.selectbox(
            "Estado*",
            ["Seleccione una opción",
            "pendiente",
            "aceptado",
            "liquidado",
            "al dia",
            "en mora",
            "en juicio",
            "cancelado",
            "finalizado"
            ],
            index=["Seleccione una opción",
            "pendiente",
            "aceptado",
            "liquidado",
            "al dia",
            "en mora",
            "en juicio",
            "cancelado",
            "finalizado"].index(estado),key=f'estadoo_{prestamo['nro']}')
        tipo_prestamo = st.radio(
            "Tipo de Préstamo*",
            ["mensual",
            "quincenal",
            "semanal"],
            index=["mensual",
                    "quincenal",
                    "semanal"].index(tipo_prestamo),key=f'tipoo_{prestamo['nro']}')
    with col2:
        cantidad_cuotas = st.number_input("Cantidad de Cuotas*",
                                            min_value=1,
                                            step=1,
                                            value=cantidad_cuotas,key=f'cantt_{prestamo['nro']}')
        capital = st.number_input("Capital*", min_value=0.0, step=1000.0, value=float(capital),key=f'capitall_{prestamo['nro']}')
        TNM=st.number_input('T.N.M*', min_value=0.0, step=0.1,value=float(TNM),key=f'tnmm_{prestamo['nro']}')
        monto=st.number_input('Monto Cuota',min_value=0.0, step=1000.0,value=float(monto),key=f'monto_{prestamo['nro']}')
        vendedor=st.selectbox('vendedor',vendedores,key=f'vendedor_{prestamo['nro']}')
    obs=st.text_input('Observaciones',value=obs,key=f'obss_{prestamo['nro']}')
    # Botón de acción dentro del formulario

    if st.button('crear',key=f'crearr_{prestamo['nro']}'):
        nuevo_prestamo = [
            max(st.session_state['prestamos']['nro'],default=0) + 1,
            str(fecha),
            nombre_cliente,
            vendedor,
            cantidad_cuotas,
            capital,
            tipo_prestamo,
            estado,
            venc_dia,
            producto_asociado,
            TNM,
            monto,
            obs,]
        #Editar préstamo existente
        st.session_state["prestamos"].loc[st.session_state["prestamos"]['nro'] == prestamo["nro"], :] = nuevo_prestamo
        save(st.session_state["prestamos"])



def display_table(search_query=None):
    st.subheader("Préstamos Registrados")

    df = st.session_state["prestamos"]

    # Filtrar datos según la consulta de búsqueda
    if search_query is not None:
        if len(search_query)==1:
            df = df[df.apply(lambda row: search_query[0].lower() in row.to_string().lower(), axis=1)]
        else:
            df[df['nombre']==search_query[0] and df['estado']==search_query[1]]
    else:
        if st.session_state['user_data']['permisos'].iloc[0]!='admin':
            df=df[df['vendedor']==st.session_state['usuario']]
    # Configuración de paginación
    ITEMS_POR_PAGINA = 10
    # Paginación
    total_paginas = (len(df) // ITEMS_POR_PAGINA) + (1 if len(df) % ITEMS_POR_PAGINA > 0 else 0)
    inicio = (st.session_state['pagina_actual'] - 1) * ITEMS_POR_PAGINA
    fin = inicio + ITEMS_POR_PAGINA
    df_paginado = df.iloc[inicio:fin]

    if not df.empty:
        updated_rows = []  # Para almacenar cambios de estado temporalmente
        for idx, row in df_paginado.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([4, 2, 1])
                with col1:
                    st.write(f"**Fecha:** {row['fecha']} |**Capital:** {row['capital']}")
                    st.write(f"**Cliente:** {row['nombre']}")
                if st.session_state['user_data']['permisos'].iloc[0]=='admin':
                    with col2:
                        new_estado = st.selectbox(
                            "Estado*", 
                            ["Seleccione una opción", "pendiente", "aceptado", "liquidado", 
                            "al dia", "en mora", "en juicio", "cancelado", "finalizado"],
                            index=["Seleccione una opción", "pendiente", "aceptado", "liquidado",
                                "al dia", "en mora", "en juicio", "cancelado", "finalizado"].index(row["estado"]),
                            key=f"estado_{idx}"
                        )
                        # Agregar cambios si el estado cambió
                        if new_estado != row["estado"]:
                            updated_rows.append((idx, new_estado))
                        with st.popover(f'✏️ Editar'):
                            editar(row)

        # Actualizar los cambios en el DataFrame
        for index, new_estado in updated_rows:
            st.session_state["prestamos"].loc[st.session_state["prestamos"]['nro']==index, "estado"] = new_estado
            save(st.session_state["prestamos"])  # Guardar cambios al archivo Excel
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




col1,col2,col3=st.columns(3)
with col1:
    st.title("Prestamos")
with col3:
    if st.session_state['user_data']['permisos'].iloc[0]=='admin':
        # Botón para crear un nuevo préstamo
        with st.popover("Crear Préstamo",use_container_width=False,icon=f'💲'):
            crear()
with st.container(border=True):
    st.subheader("Filtros")
    lista=['seleccione un cliente']
    for nombre in clientes['nombre']:
        lista.append(nombre)
    col1,col2=st.columns(2)
    querys=[]
    with col1:
        query1 = st.selectbox("Cliente",lista, key="search_query1")
    with col2:
        query2=st.selectbox(
            "Estado*",
            ["Seleccione una opción",
                "pendiente",
                "aceptado",
                "liquidado",
                "al dia",
                "en mora",
                "en juicio",
                "cancelado",
                "finalizado"],key="search_query2")
    if st.button('buscar'):
        if query1!='seleccione un cliente' and query2!='Seleccione una opción':
            querys.append(query1,query2)
        elif query1!='seleccione un cliente':
            querys.append(query1)
        elif query2!='Seleccione una opción':
            querys.append(query2)
        display_table(querys)
    
    if st.button('Resetea los filtros'):
        querys=[]
    else:
        display_table()
if st.button('Ver todos los datos'):
    st.dataframe(load())





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