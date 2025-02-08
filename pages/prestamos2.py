#esta es una versión que estuve peleando con chatgpt y no me dió muchos resultados pero por ahi algo de acá sirve, estuve viendo el tema de los datetimes

import login
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import streamlit as st
import pandas as pd

# Configuración de rutas y clientes
idc = st.secrets['ids']['prestamos']
url = st.secrets['urls']['prestamos']
clientes = login.load_data(st.secrets['urls']['clientes'])

def load():
    return login.load_data(url)

def new(datos):
    login.append_data(idc, datos)
    st.session_state['prestamos'] = load()

def save(df):
    login.save_data(idc, df)
    st.session_state['prestamos'] = load()

if 'prestamo' not in st.session_state:
    st.session_state['prestamo'] = load()
    st.session_state["prestamos"]['fecha']=st.session_state["prestamos"]['fecha'] = st.session_state["prestamos"]['fecha'].astype(str)

def generar_fechas_pagos(fecha_registro, frecuencia, cuotas, dia_semana):
    fecha_registro=datetime.strptime(fecha_registro)
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

    for _ in range(int(cuotas)):
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
    fechas = generar_fechas_pagos(data['fecha'], data['tipo'], data['cantidad'], data['vence dia'])
    for fecha in fechas:
        nueva_visita = [
            len(st.session_state['visitas']) + 1,
            'cobranza',
            st.session_state['usuario'],
            data['nombre'],
            str(fecha),
            ''
        ]
        login.append_data(st.secrets['ids']['visitas'], nueva_visita)

def crear_cobranzas(data):
    # Corrección en la clave de URL para cobranzas
    cobranzas = login.load_data(st.secrets['urls']['cobranzas'])
    
    # Extraer valores escalares de data (asumiendo que data es un DataFrame de un solo registro)
    fecha = data['fecha'].iloc[0] if isinstance(data['fecha'], pd.Series) else data['fecha']
    tipo = data['tipo'].iloc[0] if isinstance(data['tipo'], pd.Series) else data['tipo']
    cantidad = data['cantidad'].iloc[0] if isinstance(data['cantidad'], pd.Series) else data['cantidad']
    vence_dia = data['vence dia'].iloc[0] if isinstance(data['vence dia'], pd.Series) else data['vence dia']
    
    fechas = generar_fechas_pagos(fecha, tipo, cantidad, vence_dia)
    i = 0
    for fecha_pago in fechas:
        # Extraer el DNI del cliente como un valor único
        dni_cliente = clientes.loc[clientes.nombre == data['nombre'].iloc[0], 'dni'].values[0] \
                      if isinstance(data['nombre'], pd.Series) else clientes.loc[clientes.nombre == data['nombre'], 'dni'].values[0]
        nueva_cobranza = [
            len(cobranzas) + 1,
            dni_cliente,
            st.session_state['usuario'],
            data['nombre'].iloc[0] if isinstance(data['nombre'], pd.Series) else data['nombre'],
            i,
            data['monto'].iloc[0] if isinstance(data['monto'], pd.Series) else data['monto'],
            data['monto'].iloc[0] if isinstance(data['monto'], pd.Series) else data['monto'],
            0.0,
            0.0,
            str(fecha_pago),
            str(fecha_pago),
            'Pendiente de Pago'
        ]
        i += 1
        login.append_data(st.secrets['ids']['cobranzas'], nueva_cobranza)


caja = login.load_data(st.secrets['urls']['flujo_caja'])
def egreso_caja(data):
    # Se corrige el uso del f-string para evitar colisión de comillas
    mov = [
        str(data['fecha']),
        f"PLAN {data['cantidad']} CUOTAS DE {data['capital']}",
        0,
        data['capital'],
        -data['capital'],
        caja['saldo'].sum() - data['capital']
    ]
    login.append_data(st.secrets['ids']['flujo_caja'], mov)

def reporte_venta(data):
    clientes_data = login.load_data(st.secrets['urls']['clientes'])
    cliente = clientes_data[clientes_data['nombre'] == data['nombre']]
    venta = [
        st.session_state['usuario'],
        cliente['dni'].values[0],
        data['nombre'],
        data['id'],
        data['cantidad'],
        data['capital']
    ]
    login.append_data(st.secrets['ids']['repo_venta'], venta)

# Inicialización de login y estados de sesión
login.generarLogin()

if 'page' not in st.session_state:
    st.session_state["page"] = "main"  # Página por defecto

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
    total_paginas = (len(df) // ITEMS_POR_PAGINA) + (1 if len(df) % ITEMS_POR_PAGINA > 0 else 0)
    inicio = (st.session_state['pagina_actual'] - 1) * ITEMS_POR_PAGINA
    fin = inicio + ITEMS_POR_PAGINA
    df_paginado = df.iloc[inicio:fin] if not df.empty else pd.DataFrame()

    if not df.empty:
        updated_rows = []  # Para almacenar cambios de estado temporalmente
        for idx, row in df_paginado.iterrows():
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Fecha:** {row['fecha']} | **Capital:** {row['capital']}")
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
                    if new_estado != row["estado"]:
                        updated_rows.append((idx, new_estado))
                    if st.button(f'✏️ Editar', key=f'edit_{idx}'):
                        st.session_state["id"] = idx
                        st.session_state["page"] = "gestionar_prestamo"
                        st.rerun()

        # Actualizar los cambios en el DataFrame
        for idx, new_estado in updated_rows:
            st.session_state["prestamos"].loc[idx, "estado"] = new_estado
            save(st.session_state["prestamos"])  # Guardar cambios al archivo
    else:
        st.warning("No se encontraron resultados.")

    # Controles de paginación
    with st.container():
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
    with st.container():
        st.write(f"Se muestran de {inicio + 1} a {min(fin, len(df))} de {len(df)} resultados")
        items_seleccionados = st.selectbox("Por página", [10, 25, 50, 100], index=[10, 25, 50, 100].index(ITEMS_POR_PAGINA))
        if items_seleccionados != ITEMS_POR_PAGINA:
            ITEMS_POR_PAGINA = items_seleccionados
            st.session_state['pagina_actual'] = 1
            st.rerun()

# Función para guardar un nuevo préstamo
#def guardar_prestamo(data):
    #st.session_state["prestamos"] = pd.concat([st.session_state["prestamos"], data], ignore_index=True)
    #save(st.session_state["prestamos"])
    # Registrar historial para cada préstamo nuevo
    #for _, row in data.iterrows():
    #    login.historial(row, 'nuevo_prestamo')
    #crear_cobranzas(data)
    #crear_visitas(data)
    #egreso_caja(data)
    #reporte_venta(data)

# Página de lista de préstamos
if st.session_state["page"] == "main":
    st.title("Gestión de Préstamos")
    col1, col2 = st.columns(2)
    with col1:
        # Botón para crear un nuevo préstamo
        if st.button("Crear Préstamo"):
            st.session_state["id"] = None  # No se está editando ningún cliente
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
if st.session_state["page"] == "gestionar_prestamo":
    st.title("Crear Préstamo")

    # Si estamos editando un préstamo, cargar datos existentes
    if st.session_state["id"] is not None:
        prestamo = st.session_state["prestamos"].iloc[st.session_state["id"]]
        fecha = pd.to_datetime(prestamo["fecha"]).date() if prestamo["fecha"] else date.today()
        nombre_cliente_default = prestamo["nombre"]
        capital = prestamo["capital"]
        tipo_prestamo = prestamo["tipo"]
        cantidad_cuotas = prestamo["cantidad"]
        estado = prestamo["estado"]
        producto_asociado = prestamo["producto asociado"]
        TNM = prestamo['tnm']
        monto = prestamo["monto"]
        vence_dia = prestamo['vence dia']
        obs = prestamo["obs"]
    else:
        # Valores por defecto para un nuevo préstamo
        fecha = date.today()
        nombre_cliente_default = ""
        capital = 0.0
        tipo_prestamo = "mensual"
        cantidad_cuotas = 1.0
        estado = "liquidado"
        producto_asociado = ''
        TNM = 18.0
        monto = 0.0
        vence_dia = 'lunes'
        obs = ''

    # Formulario para crear o editar un préstamo
    with st.form("form_prestamo"):
        col1, col2 = st.columns(2)
        lista = ['seleccione un cliente']
        for nombre in clientes['nombre']:
            lista.append(nombre)
        with col1:
            if st.session_state["id"] is not None and nombre_cliente_default in lista:
                index_cliente = lista.index(nombre_cliente_default)
            else:
                index_cliente = 0
            nombre_cliente = st.selectbox('Cliente', lista, index=index_cliente)
            venc_dia = st.selectbox(
                'Dia Vencimiento Cuota', 
                ["Seleccione una opción", 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado'], 
                index=["Seleccione una opción", 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado'].index(vence_dia)
            )
            producto_asociado = st.text_input('Producto Asociado*', value=producto_asociado)
            estado = st.selectbox(
                "Estado*", 
                ["Seleccione una opción", "pendiente", "aceptado", "liquidado", "al dia", "en mora", "en juicio", "cancelado", "finalizado"],
                index=["Seleccione una opción", "pendiente", "aceptado", "liquidado", "al dia", "en mora", "en juicio", "cancelado", "finalizado"].index(estado)
            )
            tipo_prestamo = st.radio(
                "Tipo de Préstamo*", 
                ["mensual", "quincenal", "semanal"], 
                index=["mensual", "quincenal", "semanal"].index(tipo_prestamo)
            )
        with col2:
            cantidad_cuotas = st.number_input("Cantidad de Cuotas*", min_value=1.0, step=1.0, value=cantidad_cuotas)
            capital = st.number_input("Capital*", min_value=0.0, step=1000.0, value=float(capital))
            TNM = st.number_input('T.N.M*', min_value=0.0, step=0.1, value=TNM)
            monto = st.number_input('Monto Cuota', min_value=0.0, step=1000.0, value=monto)
        obs = st.text_input('Observaciones', value=obs)
        # Botón de acción dentro del formulario
        crear = st.form_submit_button("Crear")

    # Botón para volver a la lista de clientes
    if st.button("Cancelar"):
        st.session_state["page"] = "main"  # Regresar a la página de lista
        st.rerun()  # Forzar la redirección

    # Manejo del evento al enviar el formulario
    if crear:
        if not (nombre_cliente and estado != "Seleccione una opción" and monto != 0.0 and TNM != 0 and capital != 0.0):
            st.error("Por favor, complete todos los campos obligatorios marcados con *.")
        else:
            nuevo_prestamo = pd.DataFrame([{
                "fecha": str(fecha),
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
            if st.session_state["id"] is not None:
                # Editar préstamo existente
                st.session_state["prestamos"].iloc[st.session_state["id"]] = nuevo_prestamo.iloc[0]
                login.historial(st.session_state["prestamos"].iloc[st.session_state["id"]].to_dict(), 'edicion_prestamo_viejo')
                save(st.session_state["prestamos"])
                login.historial(nuevo_prestamo.iloc[0].to_dict(), 'edicion_prestamo_nuevo')
            else:
                pass
            st.session_state["page"] = "main"
            st.rerun()

# Opciones adicionales para el usuario "admin": carga de archivos CSV
if st.session_state['usuario'] == "admin":
    st.title("Subir nuevos datos")
    st.title("Cargar y analizar archivo CSV")

    uploaded_file = st.file_uploader("Sube un archivo CSV", type="csv")

    if uploaded_file is not None:
        df_csv = pd.read_csv(uploaded_file)
        st.success("Archivo cargado con éxito!")
        st.subheader("Vista previa de los datos:")
        st.dataframe(df_csv.head())
        st.subheader("Descripción estadística:")
        st.write(df_csv.describe())
        st.subheader("Columnas del archivo:")
        st.write(df_csv.columns.tolist())
    else:
        st.info("Por favor, sube un archivo para comenzar.")