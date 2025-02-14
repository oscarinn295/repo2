#este es use porque me estaban faltando los datos de estado de la cobranza entonces queria reemplazar todo automaticamente, por si vuelve a servir, no tocar
import streamlit as st
import login
import pandas as pd
from datetime import date

# Cargar datos
cobranzas = login.load_data(st.secrets['urls']['cobranzas'])

# Rellenar valores nulos con un espacio
#cobranzas.fillna(' ', inplace=True)

# Asegurar que la columna 'vencimiento' sea de tipo date
cobranzas['vencimiento'] = pd.to_datetime(cobranzas['vencimiento']).dt.date

# Actualizar estado a 'pago total' si 'fecha_cobro' no es nula
#cobranzas.loc[cobranzas['fecha_cobro']==' ' , 'estado'] = 'pago total'

# Actualizar el estado correctamente
#cobranzas.loc[
#    (cobranzas['vencimiento'] < date.today()) & 
#    (~cobranzas['estado'].isin(['pago total', 'pago parcial', 'en mora'])), 
#    'estado'
#] = 'en mora'

# Actualizar el estado correctamente
#cobranzas.loc[
#    (cobranzas['vencimiento'] > date.today()), 
#    'estado'
#] = 'pendiente de pago'
# Convertir DataFrame a lista de listas
#lista = [cobranzas.columns.tolist()] + cobranzas.values.tolist()

# Enviar datos corregidos a Google Sheets
#y por si se llegase a ejecutar, comente la linea
#login.overwrite_sheet(lista, st.secrets['ids']['cobranzas'])

def calcular_recargo():
    tipo_prestamo = {'mensual': 300, 'semanal': 400, 'quincenal': 500}
    hoy = date.today()
    prestamos=login.load_data(st.secrets['urls']['prestamos'])
    def calcular_fila(cobranza):
        prestamo=prestamos[prestamos['id']==cobranza['prestamo_id']]
        diff = (hoy - cobranza['vencimiento']).days
        
        return tipo_prestamo.get(prestamo.iloc[0]['tipo'], 0) * diff
    cobranzas['mora'] =cobranzas.apply(calcular_fila, axis=1)
calcular_recargo()

# Mostrar DataFrame en Streamlit
st.dataframe(cobranzas)