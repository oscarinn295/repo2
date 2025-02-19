import streamlit as st
import login
import pandas as pd

idc=st.secrets['ids']['parametros']
url=st.secrets['urls']['parametros']
def load():
    return login.load_data(url)

def save(id,column,data):#modifica un solo dato
    login.save_data(id,column,data,idc)




login.generarLogin()



# Datos iniciales en caso de que el archivo no exista
DEFAULT_DATA = [
    {"Parametro": "Comisión Vendedores Por Cobranza Total de cartera (%)", "Valor": 10.0},
    {"Parametro": "Tasa de Interes Anual por Mora (%)", "Valor": 360.0},
    {"Parametro": "Comisión Monto Objetivo de Venta ($)", "Valor": 10000.0},
    {"Parametro": "Comisión del Monto objetivo (%)", "Valor": 10.0},
    {'Parametro':'Recargo por mora semanal',"Valor": 300.0},
    {'Parametro':'Recargo por mora quincenal',"Valor": 400.0},
    {'Parametro':'Recargo por mora mensual',"Valor": 500.0},]


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
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.write(f"**{row['parametro']}**")
            with col2:
                nuevo_valor = st.number_input(
                    "Valor",
                    value=row["valor"],
                    key=f"valor_{idx}"
                )
            with col3:
                if st.button("Editar", key=f"editar_{idx}"):
                    df.at[idx, "Valor"] = nuevo_valor
                    save(df)
                    st.success(f"Parámetro actualizado: {row['Parametro']}")
                    st.rerun()
else:
    st.warning("No se encontraron resultados.")
