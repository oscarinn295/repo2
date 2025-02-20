import streamlit as st
import login
import datetime as dt
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import math

#inicializando los datos de los prestamos
idc=st.secrets['ids']['prestamos']
url=st.secrets['urls']['prestamos']

def load():
    return login.load_data_vendedores(url)

def delete(index):#borra una fila completa y acomoda el resto de la hoja para que no quede el espacio en blanco
    login.delete_data(index,idc)
def save(id,column,data):#modifica un solo dato
    login.save_data(id,column,data,idc)
def new(data):#añade una columna entera de datos
    login.append_data(data,idc)


if 'usuario' not in st.session_state:
    st.switch_page('inicio.py')
login.generarLogin()


st.session_state['prestamos']=load()

def save_data(id_value, column_name, new_value, sheet_id):
    worksheet = login.get_worksheet(sheet_id)
    col_labels = worksheet.row_values(1)

    if column_name not in col_labels:
        return
    
    col_index = col_labels.index(column_name) + 1
    id_column_values = worksheet.col_values(1)  # Se asume que la columna "ID" siempre es la primera
    
    if str(id_value) in id_column_values:
        row_index = id_column_values.index(str(id_value)) + 1
        worksheet.update_cell(row_index, col_index, new_value)

def save2(id,col,val):
    save_data(id,col,val,idc)




if "mov" not in st.session_state:
    st.session_state["mov"] = login.load_data(st.secrets['urls']['flujo_caja'])

if "cobranzas" not in st.session_state:
    st.session_state["cobranzas"] = login.load_data_vendedores(st.secrets['urls']['cobranzas'])

if "clientes" not in st.session_state:
    st.session_state["clientes"] = login.load_data_vendedores(st.secrets['urls']['clientes'])


cobranzas=st.session_state["cobranzas"]
clientes=st.session_state["clientes"]

import numpy as np
def display_table():

    df = st.session_state["prestamos"]
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
                    st.write(f"**Fecha:** {row['fecha']} \n", unsafe_allow_html=True)
                    st.write(f"**Concepto:** {row['asociado']} \n", unsafe_allow_html=True)
                    st.write(f"**Capital:** ${row['capital']:,.2f} \n ", unsafe_allow_html=True)
                    st.write(f"**Monto por cuota:** ${row['monto']:,.2f} \n ", unsafe_allow_html=True)
                    if not(row['redondeo'] in [np.nan,'',0]):
                        st.write(f"**Redondeo:** ${row['redondeo']:,.2f}", unsafe_allow_html=True)


                if st.session_state['user_data']['permisos'].iloc[0]=='admin':
                    with col2:
                        st.write(f"**Cliente:** {row['nombre']}\n", unsafe_allow_html=True)
                        st.write(f"**Nro de cuotas:** {int(row['cantidad'])}")
                    with col3:
                        st.write(f"vendedor:{row['vendedor']}\n", unsafe_allow_html=True)
                        st.write(f"vencimiento:{row['vence']}")
                    with col4:
                        new_estado = st.selectbox(
                            "Estado*", 
                            ["Seleccione una opción", "pendiente", "aceptado", "liquidado", 
                            "al dia", "En mora", "en juicio", "cancelado", "finalizado"],
                            index=["Seleccione una opción", "pendiente", "aceptado", "liquidado",
                                "al dia", "En mora", "en juicio", "cancelado", "finalizado"].index(row["estado"]),
                            key=f"estado_{idx}"
                        )
                        # Agregar cambios si el estado cambió
                        if new_estado != row["estado"]:
                            save2(row['id'],'estado',new_estado)
                            st.session_state['prestamos']=load()
                            st.rerun()
                        #with st.popover(f'✏️ Editar'):
                            #editar(row)
                else:
                    with col2:
                        st.write(f"**Cliente:** {row['nombre']}\n", unsafe_allow_html=True)
                        st.write(f"**Nro de cuotas:** {row['cantidad']}")
                    with col3:
                        st.write(f"vencimiento:{row['vence']}\n", unsafe_allow_html=True)
                        st.write(f"{row['estado']}")
    else:
        st.warning("No se encontraron resultados.")