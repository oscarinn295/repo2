import streamlit as st
import login
from datetime import datetime
from datetime import date
import datetime as dt
from dateutil.relativedelta import relativedelta


if "cobranzas" not in st.session_state:
    st.session_state["cobranzas"] = login.load_data(st.secrets['urls']['cobranzas'])
cobranzas=st.session_state["cobranzas"]


if "mov" not in st.session_state:
    st.session_state["mov"] = login.load_data(st.secrets['urls']['flujo_caja'])


if "clientes" not in st.session_state:
    st.session_state["clientes"] = login.load_data(st.secrets['urls']['clientes'])
clientes=st.session_state["clientes"]


#funciones que generan datos fuera de esta pagina
def generar_fechas_prestamos(fecha_registro:str, frecuencia:str, cuotas:int):
    """
    Genera fechas de pago a partir de las condiciones dadas.
    :param fecha_registro: que originalmente es un datetime pero como que no me estaba dejando guardar datetime
        así que primero son los strings que salen de eso
        los string de fecha para este caso tienen que venir con este formato %d/%m/%Y
    :param frecuencia: Frecuencia de pago ('semanal', 'quincenal', 'mensual')
    :param cuotas: Número de cuotas
    :return: Lista de fechas de pago (list of datetime.date)
    """
    fecha_registro=datetime.strptime(fecha_registro, "%Y-%m-%d")
    fecha_actual=fecha_registro
    fechas=[]

    semanales={
        'Semanal: lunes':0,
        'Semanal: martes':1,
        'Semanal: miercoles':2,
        'Semanal: jueves':3,
        'Semanal: viernes':4,
        'Semanal: sabado':5}
    
    if frecuencia=='Mensual: 1-10':
        fecha_actual+=dt.timedelta(days=10-date.today().day)
        for _ in range(cuotas):
            fecha_actual+=relativedelta(months=1)
            fechas.append(fecha_actual.strftime("%Y-%m-%d"))

    elif frecuencia=='Mensual: 10-20':
        fecha_actual+=dt.timedelta(days=20-date.today().day)
        for _ in range(cuotas):
            fecha_actual+=relativedelta(months=1)
            fechas.append(fecha_actual.strftime("%Y-%m-%d"))


    elif frecuencia=='Mensual: 20-30':
        fecha_actual+=dt.timedelta(days=30-date.today().day)
        for _ in range(cuotas):
            fecha_actual+=relativedelta(months=1)
            fechas.append(fecha_actual.strftime("%Y-%m-%d"))

    elif frecuencia=='Quincenal':
        for _ in range(cuotas):
            fecha_actual+=dt.timedelta(weeks=2)
            fechas.append(fecha_actual.strftime("%Y-%m-%d"))

    elif frecuencia in semanales:
        dia_objetivo = semanales[frecuencia]
        while fecha_actual.weekday() != dia_objetivo:
            fecha_actual += dt.timedelta(days=1)
        for _ in range(cuotas):
            fecha_actual+=dt.timedelta(weeks=1)
            fechas.append(fecha_actual.strftime("%Y-%m-%d"))
    else:
        return date.today().strftime("%Y-%m-%d")
    return fechas

def crear_cobranzas(data,vencimiento=None):
    fechas=generar_fechas_prestamos(data[1],data[6], data[4])
    i=1
    for fecha in fechas:
        nueva_cobranza=[
            int(st.session_state['cobranzas']['id'].max())+i,
            data[3],
            data[2],
            int(i),
            float(data[10]),
            fecha,
            0,
            0,
            float(data[10]),
            0.0,
            0.0,
            'pendiente de pago',
            '',
            data[0],
            '',
            ''
            ]
        i+=1
        login.append_data(nueva_cobranza,st.secrets['ids']['cobranzas'])

def egreso_caja(data):
    caja=st.session_state["mov"]
    caja['saldo'] = pd.to_numeric(caja['saldo'], errors='coerce')
    mov=[
        data[1],
        f"ENTREGA {data[5]}, PLAN {data[4]} CUOTAS DE {data[10]}",
        0,
        data[5],
        -data[5],
        caja['saldo'].sum()-data[5]
        ]
    login.append_data(mov,st.secrets['ids']['flujo_caja'])


def reporte_venta(data):
    venta=[
        str(data[3]),
        str(data[1]),
        str(data[2]),
        int(data[0]),
        int(data[4]),
        float(data[5])
        ]
    login.append_data(venta,st.secrets['ids']['repo_ventas'])





import pandas as pd
#inicializando los datos de los prestamos
idc=st.secrets['ids']['prestamos']
url=st.secrets['urls']['prestamos']

def load():
    return login.load_data(url)
def delete(index):#borra una fila completa y acomoda el resto de la hoja para que no quede el espacio en blanco
    login.delete_data(index,idc)
def save(id,column,data):#modifica un solo dato
    login.save_data(id,column,data,idc)
def new(data):#añade una columna entera de datos
    login.append_data(data,idc)


login.generarLogin()


st.session_state['prestamos']=load()

if 'page' not in st.session_state:
    st.session_state["page"] = "main"  # Página por defecto

if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1



vendedores=st.session_state['usuarios']['usuario'].tolist()




import math


def redondear_mil_condicional(numero, umbral=50):
    resto = numero % 1000  # Obtiene los últimos tres dígitos
    if resto < umbral:
        return int(math.floor(numero / 100) * 100)  # Redondea hacia abajo
    else:
        return int(math.ceil(numero / 100) * 100)   # Redondea hacia arriba


#formulario para crear prestamo
def crear(): 
    col1,col2=st.columns(2)
    IVA=0.21
    with col1:
        cantidad_cuotas = st.number_input("Cantidad de Cuotas*",
                                                    min_value=1,
                                                    step=1,key='cant')
        capital = st.number_input("Capital*", min_value=0.0, step=1000.0,key='capital')
    with col2:
        TNM=st.number_input('T.N.M*', min_value=0.1, step=0.1,key='tnm')
        tasa_decimal = TNM / 100
        cuota_pura=capital*((((1+tasa_decimal)**cantidad_cuotas)*tasa_decimal)/(((1+tasa_decimal)**cantidad_cuotas)-1))
        iva=cuota_pura*IVA
        interes=capital*tasa_decimal
        amortizacion=cuota_pura-interes
        monto=0.0
        if st.checkbox('calcular monto por cuota'):
            monto_final=interes+amortizacion+iva
            monto_final=redondear_mil_condicional(monto_final)
            st.write(monto_final)
        else:
            monto_final=st.number_input('Monto Cuota',min_value=0.0, step=1000.0,key='monto',value=monto)
    with st.form('crear_prestamo'):
        fecha =  date.today()
        col1, col2 = st.columns(2)
        lista=['seleccione un cliente']
        for nombre in clientes['nombre']:
            lista.append(nombre)
        with col1:
            nombre_cliente = st.selectbox('Cliente',lista)
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
        with col2:
            vendedor=st.selectbox('vendedor',vendedores)
            venc_dia=st.selectbox("Selecciona un tipo de vencimiento", ['Mensual: 1-10',
                                                                              'Mensual: 10-20',
                                                                              'Mensual: 20-30',
                                                                              'Quincenal',
                                                                              'Semanal: lunes',
                                                                              'Semanal: martes',
                                                                              'Semanal: miercoles',
                                                                              'Semanal: jueves',
                                                                              'Semanal: viernes',
                                                                              'Semanal: sabado',
                                                                              'indef']) 
        obs=st.text_input('Observaciones',key='obss')
        col1, col2 = st.columns(2)
        submit_button=st.form_submit_button('crear')
    
    if submit_button:
        nuevo_prestamo = [max(st.session_state['prestamos']['id'],default=0) + 1,
            fecha.strftime('%Y-%m-%d'),
            nombre_cliente,
            vendedor,
            cantidad_cuotas,
            capital,
            venc_dia,
            estado,
            producto_asociado,
            TNM,
            monto_final,
            obs]
        new(nuevo_prestamo)
        egreso_caja(nuevo_prestamo)
        reporte_venta(nuevo_prestamo)
        crear_cobranzas(nuevo_prestamo)
        login.historial(['nuevo prestamo','fecha','nombre','vendedor','cantidad','capital','vencimiento','estado','asociado','tnm','monto','obs'],nuevo_prestamo)

#formulario de edición de prestamos, prestamo es un df de pandas de una fila
def editar(prestamo):    # Si estamos editando un préstamo, cargar datos existentes
    with st.form(f'editar_prestamo_{prestamo['id']}'):
        fecha = pd.to_datetime(prestamo["fecha"]).date() if prestamo["fecha"] else date.today()
        nombre_cliente = prestamo["nombre"]
        capital = prestamo["capital"]
        cantidad_cuotas = prestamo["cantidad"]
        estado = prestamo["estado"]
        producto_asociado=prestamo["asociado"]
        TNM=prestamo['tnm']
        monto=prestamo["monto"]
        obs=prestamo["obs"]
        col1, col2 = st.columns(2)
        with col1:
            st.write(f'{prestamo['nombre']}')
            producto_asociado=st.text_input('Producto Asociado*',value=producto_asociado,key=f'producto_{prestamo['id']}')
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
                "finalizado"].index(estado),key=f'estadoo_{prestamo['id']}')
        with col2:
            cantidad_cuotas = st.number_input("Cantidad de Cuotas*",
                                                min_value=1,
                                                step=1,
                                                value=cantidad_cuotas,key=f'cantt_{prestamo['id']}')
            capital = st.number_input("Capital*", min_value=0.0, step=1000.0, value=float(capital),key=f'capitall_{prestamo['id']}')
            TNM=st.number_input('T.N.M*', min_value=0.0, step=0.1,value=float(TNM),key=f'tnmm_{prestamo['id']}')
            monto=st.number_input('Monto Cuota',min_value=0.0, step=1000.0,value=float(monto),key=f'monto_{prestamo['id']}')
            vendedor=st.selectbox('vendedor',vendedores,key=f'vendedor_{prestamo['id']}')
        obs=st.text_input('Observaciones',value=obs,key=f'obss_{prestamo['id']}')
        # Botón de acción dentro del formulario
        submit_button=st.form_submit_button('editar')
        st.write('para eliminar prestamo eliminar del registro, con sus respectivas cobranzas (actualización pendiente)')
    if submit_button:
        nuevo_prestamo = [
            ('id',max(st.session_state['prestamos']['id'],default=0) + 1),
            ('fecha',fecha.strftime('%d/%m/%Y')),
            ('nombre',nombre_cliente),
            ('vendedor',vendedor),
            ('cantidad',cantidad_cuotas),
            ('capital',capital),
            ('estado',estado),
            ('asociado',producto_asociado),
            ('tnm',TNM),
            ('monto',monto),
            ('obs',obs)]
        for col,dato in nuevo_prestamo:
            save(prestamo['id'],col,dato)
            st.rerun()
#mostrar los prestamos vigentes con los botones interactivos


def display_table():
    df = st.session_state["prestamos"]
    if st.session_state['user_data']['permisos'].iloc[0]!='admin':
            df=df[df['vendedor']==st.session_state['usuario']]
    else:
        lista=['seleccione un cliente']
        lista2=['seleccione un vendedor']
        for nombre in vendedores:
            lista2.append(nombre)
        for nombre in clientes['nombre']:
            lista.append(nombre)
        nombre_cliente = st.selectbox('Cliente',lista,index=0)
        vendedor=st.selectbox('vendedor',lista2,index=0)
        if nombre_cliente!='seleccione un cliente':
            st.session_state["prestamos_df"]=df[df['nombre']==nombre_cliente]
            df=st.session_state["prestamos_df"]
        if vendedor!='seleccione un vendedor':
            st.session_state["prestamos_df"]=df[df['vendedor']==vendedor]
            df=st.session_state["prestamos_df"]

    # Configuración de paginación
    ITEMS_POR_PAGINA = 10
    # Paginación
    total_paginas = (len(df) // ITEMS_POR_PAGINA) + (1 if len(df) % ITEMS_POR_PAGINA > 0 else 0)
    inicio = (st.session_state['pagina_actual'] - 1) * ITEMS_POR_PAGINA
    fin = inicio + ITEMS_POR_PAGINA
    df_paginado = df.iloc[inicio:fin]
    if not df.empty:
        for idx, row in df_paginado.iterrows():
            with st.container(border=True):
                col1, col2, col3,col4 = st.columns(4)
                with col1:
                    st.write(f"**Fecha:** {str(row['fecha'])[0:10]} |**Capital:** {row['capital']}")
                if st.session_state['user_data']['permisos'].iloc[0]=='admin':
                    with col2:
                        st.write(f"**Cliente:** {row['nombre']}")
                        st.write(f"**Nro de cuotas:** {row['cantidad']}")
                    with col3:
                        st.write(f"vendedor:{row['vendedor']}")
                        st.write(f"vencimiento:{row['vence']}")
                    with col4:
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
                            save(row['id'],'estado',new_estado)
                            st.rerun()
                        #with st.popover(f'✏️ Editar'):
                            #editar(row)
                else:
                    with col2:
                        st.write(f"**Cliente:** {row['nombre']}")
                    with col3:
                        st.write(f"**Nro de cuotas:** {row['cantidad']}")
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
    with st.expander('datos filtrados'):
        st.subheader("Datos filtrados")
        st.dataframe(df)
    with st.expander('ver morosos'):
        st.subheader("morosos")
        moras=cobranzas[cobranzas['estado']=='en mora']
        morosos=df[df['id'].isin(moras['prestamo_id'].unique())]
        st.dataframe(morosos)

col1,col2,col3=st.columns(3)
with col1:
    st.title("Prestamos")
with col3:
    if st.session_state['user_data']['permisos'].iloc[0]=='admin':
        # Botón para crear un nuevo préstamo
        with st.popover("Crear Préstamo",use_container_width=False,icon=f'💲'):
            crear()
with st.container(border=True):

    display_table()
with st.expander('Ver todos los datos'):
    st.dataframe(load())