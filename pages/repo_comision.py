import login
import streamlit as st
import pandas as pd

if 'usuario' not in st.session_state:
    st.switch_page('inicio.py')
# Llamar al módulo de login
login.generarLogin()
idc=st.secrets['ids']['repo_comision']
url=st.secrets['urls']['repo_comision']
def load():
    return login.load_data(url)

if 'comisiones' not in st.session_state:
    st.session_state['comisiones']=load()
prestamos=login.load_data(st.secrets['urls']['prestamos'])
cobranzas=login.load_data(st.secrets['urls']['cobranzas'])



def venta(vendedor,total,porcentaje,objetivo):
    caja=[vendedor,
          f'OBTIENE EL{porcentaje} DE {total} YA QUE LLEGO AL OBJETIVO DE VENTA DE {objetivo}',
          total*porcentaje
    ]
    login.append_data(caja)

def cobro(vendedor,total,porcentaje,objetivo):
    caja=[vendedor,
          f'OBTIENE EL{porcentaje} DE {total} YA QUE LLEGO AL OBJETIVO DE VENTA DE {objetivo}',
          total*porcentaje
    ]
    login.append_data(caja)


import datetime

hoy = datetime.date.today()
ayer=hoy-datetime.timedelta(days=1)
if hoy.day == 1:
    
    anho=int(ayer.year)
    mes=int(ayer.month)


    prestamos['fecha'] = pd.to_datetime(prestamos['fecha'], format="%d-%m-%Y")

    cobranzas['fecha_cobro'] = pd.to_datetime(cobranzas['fecha'], format="%d-%m-%Y")


    # Filtrar el DataFrame
    prestamos_filtrado = prestamos[(prestamos['fecha'].dt.year == anho) & (prestamos['fecha'].dt.month == mes)]
    
    cobranzas_filtrado = cobranzas[(cobranzas['fecha_cobro'].dt.year == anho) & (cobranzas['fecha_cobro'].dt.month == mes)]

    vendedores=login.load_data1(st.secrets['urls']['usuarios'])['usuario'].values.tolist()
    cobros=[]
    ventas=[]
    for vendedor in vendedores:
        v=float(prestamos_filtrado[prestamos_filtrado['vendedor']==vendedor].sum())
        c=float(cobranzas_filtrado[cobranzas_filtrado['cobrador']==vendedor].sum())
        ventas.append(vendedor,v)
        cobros.append(vendedor,c)
        if v>0:
            porcentaje=0.3
            objetivo='base'
            venta(vendedor,v,porcentaje,objetivo)
        elif v>2000000:
            porcentaje=0.4
            objetivo='2 millones'
            venta(vendedor,v,porcentaje,objetivo)
        elif v> 3500000:
            porcentaje=0.5
            objetivo='3.5 millones'
            venta(vendedor,v,porcentaje,objetivo)
        elif v>5000000:
            porcentaje=0.55
            objetivo='5 millones'
            venta(vendedor,v,porcentaje,objetivo)
        else:
            pass
        if c>3000000:
            porcentaje=0.25
            objetivo='3 millones'
            cobro(vendedor,c,porcentaje,objetivo)
        else:
            pass

        
# Función para mostrar la tabla con filtro de búsqueda
def display_table(search_query=""):
    st.subheader("Lista de Movimientos")
    df=st.session_state['comisiones']
    # Mostrar tabla en Streamlit
    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("No se encontraron resultados.")

st.title("Comisiones")
display_table()
