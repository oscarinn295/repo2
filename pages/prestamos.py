import login
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import streamlit as st

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


def display_table(search_query=""):
    st.subheader("Préstamos Registrados")

    df = st.session_state["prestamos"]

    # Filtrar datos según la consulta de búsqueda
    if search_query:
        df = df[df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)]
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
                        updated_rows.append((index, new_estado))
                    if st.button(f'✏️ Editar', key=f'edit_{idx}'):
                        st.session_state["nro"] = idx
                        st.session_state["page"] = "gestionar_prestamo"
                        st.rerun()

        # Actualizar los cambios en el DataFrame
        for index, new_estado in updated_rows:
            st.session_state["prestamos"].loc[index, "estado"] = new_estado
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

# Función para guardar un nuevo préstamo
def guardar_prestamo(data):
    st.session_state["prestamos"]=load()
    #login.historial(data,'nuevo _prestamo')

# Página de lista de préstamos
if st.session_state["page"] == "main":
    st.session_state["nro"] = None
    st.title("Gestión de Préstamos")
    col1,col2=st.columns(2)
    with col1:
        # Botón para crear un nuevo préstamo
        if st.button("Crear Préstamo"):
            st.session_state["page"] = "gestionar_prestamo"
            st.rerun()
    with col2:
        # Botón para reiniciar datos
        if st.button("Reiniciar datos"):
            st.session_state["prestamos"] = load()
            st.success("Datos reiniciados.")
    # Barra de búsqueda
    search_query = st.text_input("Buscar cliente (por cualquier campo)", key="search_query")
    display_table(search_query)
    if st.button('Ver todos los datos'):
        st.dataframe(load())




#gestionar prestamos, funciones
def generar_fechas_prestamos(fecha_registro:str, frecuencia:str, cuotas:int,vencimiento):
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
    fecha_registro=datetime.strptime(fecha_registro, "%d/%m/%Y")
    fecha_actual=fecha_registro
    if frecuencia=='mensual':
        if int(fecha_registro.dt.day())<vencimiento:
            fecha_objetivo=fecha_registro+datetime.timedelta(months=1)+ datetime.timedelta(days=vencimiento-fecha_registro.dt.day())
        else:
            fecha_objetivo=fecha_actual
        fechas=[]
        for _ in range(cuotas):
            fechas.append(fecha_objetivo.strftime("%d/%m/%Y"))
            fecha_objetivo+=datetime.timedelta(months=1)
        return fechas
    elif frecuencia=='quincenal':
        if int(fecha_registro.dt.day())<vencimiento:
            while int(fecha_actual.dt.day()) != vencimiento:
                    fecha_actual += datetime.timedelta(days=1)
        else:
            pass
        fechas=[]
        for _ in range(cuotas):
            fechas.append(fecha_objetivo.strftime("%d/%m/%Y"))
            fecha_objetivo+=datetime.timedelta(days=15)
    elif frecuencia=='semanal':
        dias_semana = {'lunes': 0, 'martes': 1, 'miércoles': 2, 'jueves': 3, 'viernes': 4, 'sábado': 5}
        if vencimiento not in dias_semana:
            raise ValueError("El día de la semana debe ser uno de: 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'")
        else:
            dia_objetivo = dias_semana[vencimiento]
        fechas = []
        if int(fecha_actual.weekday()) < dia_objetivo:
            fecha_actual+=datetime.timedelta(weeks=1)
            while fecha_actual.weekday() != dia_objetivo:
                    fecha_actual += datetime.timedelta(days=1)
        elif int(fecha_actual.weekday()) > dia_objetivo:
            while fecha_actual.weekday() != dia_objetivo:
                    fecha_actual += datetime.timedelta(days=1)
            fecha_actual+=datetime.timedelta(weeks=1)
        for _ in range(int(cuotas)):      
            fechas.append(fecha_actual.strftime("%d/%m/%Y"))
            fecha_actual+=datetime.timedelta(months=1)

def crear_visitas(data):
    st.session_state['visitas']=login.load_data(st.secrets['urls']['visitas'])
    fechas=generar_fechas_prestamos()
    for fecha in fechas:
        nueva_visita=[len(st.session_state['visitas'])+1,
                      'cobranza',
                      st.session_state['usuario'],
                      data['nombre'],
                      fecha,
                      ''
                      ]
        #primero vamos a ver que tan necesario es crear la visita antes del vencimiento de una cobranza
def crear_cobranzas(data):
    if type(fecha)==str:
        fecha=datetime.srtptime(fecha, "%d/%m/%Y")
    st.session_state['cobranzas']=login.load_data(st.secrets['urls']['cobranzas'])
    fechas=generar_fechas_prestamos(data['fecha'],data['tipo'], data['cantidad'],data['vence dia'])
    i=0
    for fecha in fechas:
        nueva_cobranza=[
            len(st.session_state['cobranzas'])+1,
            clientes[clientes.nombre==data['nombre']]['dni'],
            st.session_state['usuario'],
            data['nombre'],
            i,
            data['monto'],
            data['monto'],
            0.0,
            0.0,
            fecha,
            fecha+datetime.timedelta(weeks=7),
            'Pendiente de Pago'
            ]
        i+=1
        login.append_data(nueva_cobranza,st.secrets['ids']['cobranzas'])
def egreso_caja(data):
    st.session_state["mov"]=login.load_data(st.secrets['urls']['flujo_caja'])
    caja=st.session_state["mov"]
    mov=[
        data[1],
        f"PLAN {data['cantidad']} CUOTAS DE {data[4]}",
        0,
        data[4],
        -data[4],
        caja['saldo'].sum()-data[4]
        ]
    login.append_data(mov,st.secrets['ids']['flujo_caja'])
def reporte_venta(data):
    st.session_state["repo_ventas"]=login.load_data(st.secrets['urls']['repo_ventas'])
    clientes=login.load_data(st.secrets['urls']['clientes'])
    cliente=clientes[clientes['nombre']==data[2]]
    venta=[
        st.session_state['usuario'],
        cliente['dni'],
        data[2],
        data[0],
        data[3],
        data[4]
        ]
    login.append_data(venta,st.secrets['ids']['repo_ventas'])





# Página de gestión de préstamos
if st.session_state["page"] == "gestionar_prestamo":
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
        producto_asociado=prestamo["producto asociado"]
        TNM=prestamo['tnm']
        monto=prestamo["monto"]
        vence_dia=prestamo['vence dia']
        obs=prestamo["obs"]
    else:
        # Valores por defecto para un nuevo préstamo
        fecha = date.today()
        nombre_cliente = ""
        capital = 0.0
        tipo_prestamo = "mensual"
        cantidad_cuotas = 1.0
        estado = "liquidado"
        producto_asociado=''
        TNM=18.0
        monto=0.0
        vence_dia='lunes'
        obs=''

    # Formulario para crear o editar un préstamo
    with st.form("form_prestamo"):
        col1, col2 = st.columns(2)
        lista=['seleccione un cliente']
        for nombre in clientes['nombre']:
            lista.append(nombre)
        with col1:
            nombre_cliente = st.selectbox('Cliente',lista,index=lista.index(prestamo['nombre']) if st.session_state["nro"] is not None else 0) 
            venc_dia=st.selectbox('Dia Vencimiento Cuota',["Seleccione una opción",'lunes','martes','miercoles','jueves','viernes','sabado'],index=["Seleccione una opción",'lunes','martes','miercoles','jueves','viernes','sabado'].index(vence_dia))
            producto_asociado=st.text_input('Producto Asociado*',value=producto_asociado)
            estado = st.selectbox("Estado*", ["Seleccione una opción", "pendiente","aceptado","liquidado","al dia","en mora","en juicio","cancelado","finalizado"], index=["Seleccione una opción", "pendiente","aceptado","liquidado","al dia","en mora","en juicio","cancelado","finalizado"].index(estado))
            tipo_prestamo = st.radio("Tipo de Préstamo*", ["mensual", "quincenal", "semanal"], index=["mensual", "quincenal", "semanal"].index(tipo_prestamo))
            
        with col2:
            cantidad_cuotas = st.number_input("Cantidad de Cuotas*", min_value=1.0, step=1.0, value=cantidad_cuotas)
            capital = st.number_input("Capital*", min_value=0.0, step=1000.0, value=float(capital))
            TNM=st.number_input('T.N.M*', min_value=0.0, step=0.1,value=TNM)
            monto=st.number_input('Monto Cuota',min_value=0.0, step=1000.0,value=monto)
        obs=st.text_input('Observaciones',value=obs)
        # Botón de acción dentro del formulario
        crear = st.form_submit_button("Crear")

    # Botón para volver a la lista de clientes
    if st.button("Cancelar"):
        st.session_state["page"] = "main"  # Regresar a la página de lista
        st.rerun()  # Forzar la redirección
    # Manejo del evento al enviar el formulario
    if crear:
        nuevo_prestamo = [
            max(st.session_state['prestamos']['nro'],default=0) + 1,
            str(fecha),
            nombre_cliente,
            cantidad_cuotas,
            capital,
            tipo_prestamo,
            estado,
            venc_dia,
            producto_asociado,
            TNM,
            monto,
            obs,]
        if st.session_state["nro"] is None:
            new(nuevo_prestamo)
            egreso_caja(nuevo_prestamo)
            reporte_venta(nuevo_prestamo)
        else:
            #Editar préstamo existente
            st.session_state["prestamos"].loc['nro'==st.session_state["nro"]] = nuevo_prestamo
            save(st.session_state["prestamos"])
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