import pandas as pd
import login
import streamlit as st


idc=st.secrets['ids']['clientes']
url=st.secrets['urls']['clientes']
def load():
    return login.load_data(url)

def new(datos):
    login.append_data(datos,idc)
    st.session_state['clientes']=load()
def save(df):
    login.save_data(idc,df)
    st.session_state['clientes']=load()


login.generarLogin()
if 'page' not in st.session_state:
    st.session_state['page']='main'
if 'clientes' not in st.session_state:
    st.session_state['clientes']=load() 
if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1
vendedores=login.load_data1(st.secrets['urls']['usuarios'])['usuario'].values.tolist()
# Función para mostrar la tabla con filtro de búsqueda
def editar(cliente):
    st.title("Editar Cliente: ")
    st.session_state["dni"] = cliente["dni"]
    st.session_state["nombre"] = cliente["nombre"]
    st.session_state["direccion"] = cliente["direccion"]
    st.session_state["celular"] = cliente["celular"]
    st.session_state["vendedor"] = cliente["vendedor"]
    st.session_state['scoring']= cliente['scoring']
    st.session_state['fecha_nac']=cliente['fecha_nac']
    st.session_state['mail']=cliente['mail']

    col1,col2=st.columns(2)
    with col1:
        dni = st.text_input("DNI", value=st.session_state.get("dni", ""),key=f'dni_{cliente['nro']}')
        nombre = st.text_input("Nombre", value=st.session_state.get("nombre", ""),key=f'nombre_{cliente['nro']}')
        fecha_nac=st.date_input("Fecha", value=st.session_state.get("fecha_nac", ""),key=f'fecha_{cliente['nro']}')
        vendedor=st.selectbox('vendedor',vendedores,key=f'vendedor_{cliente['nro']}')
    with col2:
        direccion = st.text_input("Dirección", value=st.session_state.get("direccion", ""),key=f'direccion_{cliente['nro']}')
        celular = st.text_input("Celular", value=st.session_state.get("celular", ""),key=f'celular_{cliente['nro']}')
        mail=st.text_input("Mail", value=st.session_state.get("mail", ""),key=f'mail_{cliente['nro']}')
        scoring= st.text_input("Scoring", value=st.session_state.get("scoring", ""),key=f'scoring_{cliente['nro']}')

    if st.button('guardar',key=f'guardar_{cliente['nro']}'):
        # Actualizar cliente existente
        idx = cliente['nro']
        #login.historial(st.session_state['clientes'][st.session_state['clientes']['nro']==idx],'edicion_viejo')
        st.session_state["clientes"].loc[st.session_state["clientes"]['nro']==idx, ['nombre','vendedor','scoring','direccion','fecha_nac','dni','celular','mail']] = [
            nombre,vendedor,scoring, direccion,fecha_nac,dni, celular,mail
        ]
        #login.historial(st.session_state['clientes'][st.session_state['clientes']['nro']==idx],'edicion_nuevo')
        save(st.session_state["clientes"])
        st.success("cambios guardados")

def crear():
    st.title('Crear Cliente: ')
    col1,col2=st.columns(2)
    with col1:
        dni = st.text_input("DNI")
        nombre = st.text_input("Nombre")
        fecha_nac=st.date_input("Fecha")
        vendedor=st.selectbox('vendedor',vendedores)
    with col2:
        direccion = st.text_input("Dirección")
        celular = st.text_input("Celular")
        mail=st.text_input("Mail")
        scoring= st.text_input("Scoring")
    if st.button('guardar'):
        nuevo_cliente =[max(st.session_state['clientes']['nro'])+1,
                        nombre,
                        vendedor,
                        scoring,
                        direccion,
                        fecha_nac,
                        dni,
                        celular,
                        mail
                        ]
        new(nuevo_cliente)
        st.success('cliente guardado correctamente')
    #login.historial(nuevo_cliente,'nuevo cliente')

# Función para eliminar un cliente
def delete_client(index):
    st.session_state["clientes"].drop(index=index, inplace=True)
    save(st.session_state["clientes"])
    #login.historial(st.session_state["clientes"].loc[index],'borrado')
def display_table(search_query=""):
    st.subheader("Lista de Clientes")

    # Filtrar datos según la consulta de búsqueda
    df = st.session_state["clientes"]
    if search_query:
        df = df[
            df.apply(lambda row: search_query.lower() in row.to_string().lower(), axis=1)
        ]
    # Configuración de paginación
    ITEMS_POR_PAGINA = 10
    # Paginación
    total_paginas = (len(df) // ITEMS_POR_PAGINA) + (1 if len(df) % ITEMS_POR_PAGINA > 0 else 0)
    inicio = (st.session_state['pagina_actual'] - 1) * ITEMS_POR_PAGINA
    fin = inicio + ITEMS_POR_PAGINA
    df_paginado = df.iloc[inicio:fin]
    # Crear tabla con botones
    if not df.empty:
        for idx, row in df_paginado.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([4, 1, 1])  # Distribuir columnas
                with col1:
                    st.write(f"**Nombre**: {row['nombre']} - **Vendedor**: {row['vendedor']}")
                    st.write(f"**Dirección**: {row['direccion']} - **DNI**: {row['dni']} - **Celular**: {row['celular']}")
                with st.popover(f'✏️ Editar'):
                        editar(row)
                with col3:
                    if st.button("🗑️Eliminar", key=f"delete_{row['nro']}"):
                        delete_client(idx)
                        st.rerun()
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




# Página de lista de clientes
st.title("Clientes")
col1,col2,col3,col4=st.columns(4)
with col4:
    # Botón para crear un nuevo cliente
    with st.popover("Crear cliente"):
        crear()
with col1:
    # Botón para reiniciar datos
    if st.button("Reiniciar datos"):
        st.session_state["clientes"] = load()
with st.container(border=True):
    col1,col2=st.columns(2)
    with col2:
        search_query = st.text_input("Buscar cliente", key="search_query")
    display_table(search_query)
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
        st.dataframe(df)  # Muestra las primeras filas
        # Mostrar las columnas disponibles
        st.subheader("Columnas del archivo:")
        st.write(df.columns.tolist())

    else:
        st.info("Por favor, sube un archivo para comenzar.")