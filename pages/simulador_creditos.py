import streamlit as st
import login

login.generarLogin()

st.title("Simulador Crédito")

# Entrada de datos
monto_total = st.number_input("Monto total ($):", min_value=0.0, step=100.0, format="%.2f")
plazo = st.selectbox("Plazo (Meses):", [3, 6, 9, 12])
tasa_nominal_mensual = st.number_input("Tasa nominal mensual (%):", min_value=0.0, step=0.01, format="%.2f")

# Cálculo de la cuota fija mensual usando la fórmula de anualidades
IVA=0.21
if monto_total > 0 and tasa_nominal_mensual > 0 and plazo > 0:
    tasa_decimal = tasa_nominal_mensual / 100
    cuota_pura=monto_total*((((1+tasa_decimal)**plazo)*tasa_decimal)/(((1+tasa_decimal)**plazo)-1))
    iva=cuota_pura*IVA
    interes=monto_total*tasa_decimal
    amortizacion=cuota_pura-interes
    cuota_mensual=interes+amortizacion+iva
else:
    cuota_mensual = 0.0

# Resultados
st.subheader("Resultados:")
st.write(f"Cuota fija por mes: ${cuota_mensual:,.2f}")
