import streamlit as st
import login
import pandas as pd

idc=st.secrets['ids']['parametros']
url=st.secrets['urls']['parametros']
def load():
    return login.load_data1(url)
def save(df):
    login.save_data(idc,df)
    st.session_state['prestamos']=load()


login.generarLogin()



# Datos iniciales en caso de que el archivo no exista
DEFAULT_DATA = [
    {"Parametro": "Comisión Vendedores Por Cobranza Total de cartera (%)", "Valor": 10},
    {"Parametro": "Tasa de Interes Anual por Mora (%)", "Valor": 360},
    {"Parametro": "Comisión Monto Objetivo de Venta ($)", "Valor": 10000},
    {"Parametro": "Comisión del Monto objetivo (%)", "Valor": 10},
]


# Cargar o inicializar los datos
df = load()

# Título de la aplicación
col1,col2=st.columns(2)
with col1:
    st.title("Parámetros")
with col2:
    st.title('Valor')


# Mostrar tabla interactiva
if not df.empty:
    for idx, row in df.iterrows():
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.write(f"**{row['Parametro']}**")
        with col2:
            nuevo_valor = st.number_input(
                "Valor",
                value=row["Valor"],
                key=f"valor_{idx}"
            )
        with col3:
            if st.button("Editar", key=f"editar_{idx}"):
                df.at[idx, "Valor"] = nuevo_valor
                save(df)
                st.success(f"Parámetro actualizado: {row['Parametro']}")
                st.experimental_rerun()
else:
    st.warning("No se encontraron resultados.")
