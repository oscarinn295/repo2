import pandas as pd
import login
import streamlit as st


idc=st.secrets['prueba_ids']['clientes']
url = st.secrets['prueba_urls']['clientes']
def load():
    return login.load_data(url)

def delete(index):  
    # Elimina la fila en Google Sheets
    login.delete_data(index, idc)
    
    # Recargar datos actualizados
    st.session_state['clientes'] = load()
    
    # Resetear los índices de ID
    st.session_state['clientes'].reset_index(drop=True, inplace=True)
    st.session_state['clientes']['id'] = st.session_state['clientes'].index  # Asignar nuevos IDs ordenados
    
    # Convertir `fecha_nac` a string
    st.session_state['clientes']['fecha_nac'] = st.session_state['clientes']['fecha_nac'].astype(str)
    
    # Preparar datos para sobrescribir
    df = [st.session_state['clientes'].columns.tolist()]  # Encabezados
    df += st.session_state['clientes'].values.tolist()  # Datos
    
    # Sobrescribir la hoja
    login.overwrite_sheet(df, idc)
    
    # Recargar la página
    st.rerun()

def save(id,column,data):#modifica un solo dato
    login.save_data(id,column,data,idc)
def new(data):#añade una columna entera de datos
    login.append_data(data,idc)


login.generarLogin()
st.session_state['clientes']=load() 

if 'page' not in st.session_state:
    st.session_state['page']='main'
if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1
vendedores=login.load_data1(st.secrets['prueba_urls']['usuarios'])['usuario'].values.tolist()
# Función para mostrar la tabla con filtro de búsqueda
def editar(cliente):
    idx=cliente['id']
    st.title("Editar Cliente: ")
    with st.form(f'editar_cliente_{cliente['id']}'):
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
            dni = st.text_input("DNI", value=st.session_state.get("dni", ""),key=f'dni_{idx}')
            nombre = st.text_input("Nombre", value=st.session_state.get("nombre", ""),key=f'nombre_{idx}')
            if st.session_state['fecha_nac'] is not None:
                fecha_nac=st.date_input("Fecha", value=st.session_state.get("fecha_nac", ""),key=f'fecha_{idx}')
            else:
                fecha_nac=st.date_input("Fecha",key=f'fecha_{idx}')
            vendedor=st.selectbox('vendedor',vendedores,key=f'vendedor_{idx}')
        with col2:
            direccion = st.text_input("Dirección", value=st.session_state.get("direccion", ""),key=f'direccion_{idx}')
            celular = st.text_input("Celular", value=st.session_state.get("celular", ""),key=f'celular_{idx}')
            mail=st.text_input("Mail", value=st.session_state.get("mail", ""),key=f'mail_{idx}')
            scoring= st.text_input("Scoring", value=st.session_state.get("scoring", ""),key=f'scoring_{idx}')
        submit_button=st.form_submit_button('guardar')
    if submit_button:
        #login.historial(st.session_state['clientes'][st.session_state['clientes']['id']==idx],'edicion_viejo')
        datos= [(nombre,'nombre'),
                (vendedor,'vendedor'),
                (scoring,'scoring'),
                (direccion,'direccion'),
                (fecha_nac.strftime("%Y-%m-%d"),'fecha_nac'),
                (dni,'dni'),
                (celular,'celular'),
                (mail,'mail')]
        #login.historial(st.session_state['clientes'][st.session_state['clientes']['id']==idx],'edicion_nuevo')
        for dato,col in datos:
            save(idx,col,dato)
        st.success("cambios guardados")

def crear():
    st.title('Crear Cliente: ')
    with st.form("form_crear_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            dni = st.text_input("DNI")
            nombre = st.text_input("Nombre")
            fecha_nac = st.date_input("Fecha")
            vendedor = st.selectbox('Vendedor', vendedores, key='vendedores')
        
        with col2:
            direccion = st.text_input("Dirección")
            celular = st.text_input("Celular")
            mail = st.text_input("Mail")
            scoring = st.text_input("Scoring")

        # Botón de guardar dentro del formulario
        submit_button = st.form_submit_button("Guardar")
        
        if submit_button:
            nuevo_cliente = [
                max(st.session_state['clientes']['id'])+1,
                nombre,
                vendedor,
                scoring,
                direccion,
                fecha_nac.strftime("%Y-%m-%d"),
                dni,
                celular,
                mail
            ]
            new(nuevo_cliente)
            st.success('Cliente guardado correctamente')

    #login.historial(nuevo_cliente,'nuevo cliente')

def display_table(search_query=""):
    st.subheader("Lista de Clientes")

    # Filtrar datos según la consulta de búsqueda
    
    df = st.session_state["clientes"]
    if search_query:
        df =df[df['nombre'].str.contains(search_query, case=False, na=False)]
    if st.session_state['user_data']['permisos'].iloc[0]!='admin':
        df=df[df['vendedor']==st.session_state['usuario']]

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
                col1, col2, col3 = st.columns(3)  # Distribuir columnas
                if st.session_state['user_data']['permisos'].iloc[0]=='admin':
                    with col1:
                        st.write(f"**Nombre**: {row['nombre']} - **Vendedor**: {row['vendedor']}")
                        st.write(f"**Dirección**: {row['direccion']} - **DNI**: {row['dni']} - **Celular**: {row['celular']}")
                    with col2:
                        with st.popover(f'✏️ Editar'):
                                    editar(row)
                    with col3:
                        if st.button("🗑️Eliminar", key=f"delete_{row['id']}"):
                            delete(idx)
                            st.rerun()
                else:
                    with col1:
                        st.write(f"**Nombre**: {row['nombre']}")
                    with col2:
                        st.write(f"**Dirección**: {row['direccion']}- **DNI**: {row['dni']}")
                    with col3:
                        st.write(f"**Celular**: {row['celular']}  **Mail**: {row['mail']}")

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
        items_seleccionados = st.selectbox("Por página", [10, 25, 50, 100], index=[10, 25, 50, 100].index(ITEMS_POR_PAGINA),key='seleccionados')
        if items_seleccionados != ITEMS_POR_PAGINA:
            ITEMS_POR_PAGINA = items_seleccionados
            st.session_state['pagina_actual'] = 1
            st.rerun()




# Página de lista de clientes
st.title("Clientes")
col1,col2,col3,col4=st.columns(4)
with col4:
    if st.session_state['user_data']['permisos'].iloc[0]=='admin':
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


