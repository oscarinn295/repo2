import streamlit as st
import login
import pandas as pd
import os
login.generarLogin()


# Definir ruta del archivo CSV
FILE_PATH = "parametros.csv"

# Datos iniciales en caso de que el archivo no exista
DEFAULT_DATA = [
    {"Parametro": "Comisión Vendedores Por Cobranza Total de cartera (%)", "Valor": 10},
    {"Parametro": "Tasa de Interes Anual por Mora (%)", "Valor": 360},
    {"Parametro": "Comisión Monto Objetivo de Venta ($)", "Valor": 10000},
    {"Parametro": "Comisión del Monto objetivo (%)", "Valor": 10},
]

# Cargar datos desde el archivo o usar datos predeterminados
def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH)
    else:
        return pd.DataFrame(DEFAULT_DATA)

# Guardar datos en el archivo CSV
def save_data(dataframe):
    dataframe.to_csv(FILE_PATH, index=False)

# Cargar o inicializar los datos
df = load_data()

# Título de la aplicación
st.title("Parámetros")


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
                save_data(df)
                st.success(f"Parámetro actualizado: {row['Parametro']}")
                st.experimental_rerun()
else:
    st.warning("No se encontraron resultados.")
