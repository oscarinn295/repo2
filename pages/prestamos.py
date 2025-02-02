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
    login.append_data(idc,datos)
    st.session_state['prestamos']=load()
def save(df):
    login.save_data(idc,df)
    st.session_state['prestamos']=load()


def generar_fechas_pagos(fecha_registro, frecuencia, cuotas, dia_semana):
    """
    Genera fechas de pago a partir de las condiciones dadas.

    :param fecha_registro: Fecha en la que se registra el préstamo (datetime.date)
    :param frecuencia: Frecuencia de pago ('semanal', 'quincenal', 'mensual')
    :param cuotas: Número de cuotas (int)
    :param dia_semana: Día de la semana elegido para los pagos (str: 'lunes', 'martes', ..., 'sábado')
    :return: Lista de fechas de pago (list of datetime.date)
    """
    dias_semana = {'lunes': 0, 'martes': 1, 'miércoles': 2, 'jueves': 3, 'viernes': 4, 'sábado': 5}
    if dia_semana not in dias_semana:
        raise ValueError("El día de la semana debe ser uno de: 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'")

    dia_objetivo = dias_semana[dia_semana]
    fechas = []
    fecha_actual = fecha_registro

    for _ in range(cuotas):
        # Ajustar la fecha al próximo día objetivo si no coincide
        while fecha_actual.weekday() != dia_objetivo:
            fecha_actual += datetime.timedelta(days=1)

        fechas.append(fecha_actual)

        # Incrementar según la frecuencia
        if frecuencia == 'semanal':
            fecha_actual += datetime.timedelta(weeks=1)
        elif frecuencia == 'quincenal':
            fecha_actual += datetime.timedelta(weeks=2)
        elif frecuencia == 'mensual':
            fecha_actual += relativedelta(months=1)
        else:
            raise ValueError("La frecuencia debe ser 'semanal', 'quincenal' o 'mensual'")

    return fechas



def crear_visitas(data):
    st.session_state['visitas']=login.load_data(st.secrets['urls']['visitas'])
    fechas=generar_fechas_pagos(data['fecha'],data['tipo'], data['cantidad'],data['vence dia'])
    for fecha in fechas:
        nueva_visita=pd.DataFrame([{
            "nro":len(st.session_state['visitas'])+1,
                      'visita':'cobranza',
                      'vendedor':st.session_state['usuario'],
                      'nombre':data['nombre'],
                      'fecha': fecha,
                      'notas':''
                      }])
        st.session_state["visitas"] = pd.concat([st.session_state["visitas"], nueva_visita], ignore_index=True)
        login.save_data(st.secrets['ids']['visitas'],nueva_visita)
def crear_cobranzas(data):
    st.session_state['cobranzas']=login.load_data(st.secrets['urls']['cobranzas'])
    fechas=generar_fechas_pagos(data['fecha'],data['tipo'], data['cantidad'],data['vence dia'])
    i=0
    for fecha in fechas:
        nueva_cobranza=pd.DataFrame([{
            'id':len(st.session_state['cobranzas'])+1,
            'dni':clientes[clientes.nombre==data['nombre']]['dni'],
            'vendedor/cobrador':st.session_state['usuario'],
            'cliente':data['nombre'],
            'n_cuota':i,
            'monto':data['monto'],
            'monto_recalculado_mora':data['monto'],
            'pago':0.0,
            'radondeo':0.0,
            'vencimiento':fecha,
            'visita':fecha,
            'estado':'Pendiente de Pago'
            }])
        i+=1
        st.session_state["cobranzas"] = pd.concat([st.session_state["cobranzas"], nueva_cobranza], ignore_index=True)
        login.save_data(st.secrets['ids']['cobranzas'],nueva_cobranza)
caja=login.load_data(st.secrets['urls']['flujo_caja'])
def egreso_caja(data):
    st.session_state["mov"]=login.load_data(st.secrets['urls']['flujo_caja'])
    mov=pd.DataFrame([{
        'fecha':data['fecha'],
          'concepto': f"PLAN {data['cantidad']} CUOTAS DE {data['capital']}",
          'ingreso':0,
          'egreso':data['capital'],
          'total':-data['capital'],
          'saldo':caja['saldo'].sum()-data['capital']
          }])
    st.session_state["mov"] = pd.concat([st.session_state["mov"], mov], ignore_index=True)
    login.save_data(st.secrets['ids']['mov'],mov)
def reporte_venta(data):
    st.session_state["repo_ventas"]=login.load_data(st.secrets['urls']['repo_ventas'])
    clientes=login.load_data(st.secrets['urls']['clientes'])
    cliente=clientes[clientes['nombre']==data['nombre']]
    venta=pd.DataFrame([{
        'vendedor':st.session_state['usuario'],
        'dni':cliente['dni'],
        'nombre':data['nombre'],
        'id':data['id'],
        'cantidad':data['cantidad'],
        'capital':data['capital']
        }])
    st.session_state["repo_ventas"] = pd.concat([st.session_state["repo_ventas"], venta], ignore_index=True)
    login.save_data(st.secrets['ids']['repo_ventas'],venta)

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
        nuevo_prestamo = pd.DataFrame([{
            'nro':len(st.session_state['prestamos']['nro'])+1,
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
        }])
        if st.session_state["nro"] is None:
            st.session_state["prestamos"] = pd.concat([st.session_state["prestamos"], nuevo_prestamo], ignore_index=True)
            save(st.session_state["prestamos"])
            
        else:
            # Editar préstamo existente
            st.session_state["prestamos"].iloc[st.session_state["nro"]] = nuevo_prestamo
            #login.historial(st.session_state["prestamos"].iloc[st.session_state["nro"]],'edicion_prestamo_viejo')
            save(st.session_state["prestamos"])
            #login.historial(nuevo_prestamo,'edicion_prestamo_nuevo')
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