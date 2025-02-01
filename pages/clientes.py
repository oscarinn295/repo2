import pandas as pd
import login
import streamlit as st


idc=st.secrets['ids']['clientes']
url=st.secrets['urls']['clientes']
def load():
    return login.load_data(url)

def new(datos):
    login.append_data(idc,datos)
    st.session_state['prestamos']=load()
def save(df):
    login.save_data(idc,df)
    st.session_state['prestamos']=load()


login.generarLogin()
if 'page' not in st.session_state:
    st.session_state['page']='main'
if 'clientes' not in st.session_state:
    st.session_state['clientes']=load() 
if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1
# Función para mostrar la tabla con filtro de búsqueda
# Función para mostrar la tabla con filtro de búsqueda
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
                with col2:
                    if st.button(f'✏️ Editar', key=f'edit_{idx}'):
                        st.session_state["nro"] = row["nro"]  # Guardar el número del cliente
                        st.session_state["page"] = "gestionar"  # Cambiar a la página de gestión
                        st.rerun()
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


# Función para eliminar un cliente
def delete_client(index):
    st.session_state["clientes"].drop(index=index, inplace=True)
    save(st.session_state["clientes"])
    login.historial(st.session_state["clientes"].loc[index],'borrado')

# Página de lista de clientes
if st.session_state["page"] == "main":
    st.title("Gestión de Clientes")
    col1,col2=st.columns(2)
    with col1:
        # Botón para crear un nuevo cliente
        if st.button("Crear Nuevo Cliente"):
            st.session_state["nro"] = None  # No se está editando ningún cliente
            st.session_state["page"] = "gestionar"  # Cambiar a la página de gestión
            st.rerun()  # Forzar la redirección
    with col2:
        # Botón para reiniciar datos
        if st.button("Reiniciar datos"):
            st.session_state["clientes"] = load()
    # Barra de búsqueda
    search_query = st.text_input("Buscar cliente (por cualquier campo)", key="search_query")
    display_table(search_query)
    if st.button('Ver todos los datos'):
        st.dataframe(load())

# Página de gestión de clientes
elif st.session_state["page"] == "gestionar":
    st.title("Gestión de Cliente")
    if "clientes" not in st.session_state:
        st.session_state["clientes"] = load()

    def reset_form():
        st.session_state['nro']=None
        st.session_state["dni"] = ""
        st.session_state["nombre"] = ""
        st.session_state["direccion"] = ""
        st.session_state["celular"] = ""
        st.session_state["vendedor"] = ""

    # Cargar datos del cliente en caso de edición
    if st.session_state.get("nro") is not None:
        cliente = st.session_state["clientes"].loc[
            st.session_state["clientes"]["nro"] == st.session_state["nro"]
        ].squeeze()
        st.session_state["dni"] = cliente["dni"]
        st.session_state["nombre"] = cliente["nombre"]
        st.session_state["direccion"] = cliente["direccion"]
        st.session_state["celular"] = cliente["celular"]
        st.session_state["vendedor"] = cliente["vendedor"]
    else:
        reset_form()

    # Formulario
    st.title("Formulario de Cliente")
    with st.form("Formulario Cliente"):
        dni = st.text_input("DNI", value=st.session_state.get("dni", ""))
        nombre = st.text_input("Nombre", value=st.session_state.get("nombre", ""))
        direccion = st.text_input("Dirección", value=st.session_state.get("direccion", ""))
        celular = st.text_input("Celular", value=st.session_state.get("celular", ""))
        vendedor = st.text_input("Vendedor", value=st.session_state.get("vendedor", ""))

        submit_button = st.form_submit_button("Guardar")

    # Procesar el formulario
    if submit_button:
        if st.session_state["nro"] is None:
            # Crear cliente nuevo
            nuevo_cliente = pd.DataFrame([{
                "nro":  max(st.session_state['clientes']['nro'])+1,
                "dni": dni,
                "nombre": nombre,
                "direccion": direccion,
                "celular": celular,
                "vendedor": vendedor,
            }])
            st.session_state["clientes"] = pd.concat([st.session_state["clientes"], nuevo_cliente], ignore_index=True)
            login.historial(nuevo_cliente,'nuevo cliente')
        else:
            # Actualizar cliente existente
            idx = st.session_state["nro"]
            login.historial(st.session_state['clientes'][st.session_state['clientes']['nro']==idx],'edicion_viejo')
            st.session_state["clientes"].loc[idx, ["dni", "nombre", "direccion", "celular", "vendedor"]] = [
                dni, nombre, direccion, celular, vendedor
            ]
            login.historial(st.session_state['clientes'][st.session_state['clientes']['nro']==idx],'edicion_nuevo')
        save(st.session_state["clientes"])
        st.success("Cliente guardado.")
        reset_form()
        st.rerun()

    # Botón para volver a la lista de clientes
    if st.button("Volver"):
        st.session_state["page"] = "main"  # Regresar a la página de lista
        st.rerun()  # Forzar la redirección
    
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