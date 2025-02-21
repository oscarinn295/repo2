import streamlit as st
import streamlit.components.v1 as components
import math

def redondear_mil_condicional(valor):
    """Redondea el valor al múltiplo de 1000 más cercano."""
    redondeo = 1000 - (valor % 1000) if valor % 1000 != 0 else 0
    return valor + redondeo, redondeo

def crear():
    col1, col2 = st.columns(2)
    IVA = 0.21

    with col1:
        cantidad_cuotas = st.number_input("Cantidad de Cuotas*", min_value=1, step=1, key='cant')

        # Campo de capital con formateo en vivo (JS)
        st.markdown("#### Capital:")
        capital_html = """
        <input type="text" id="capitalInput" placeholder="$0.00" style="width: 100%; font-size: 20px; text-align: right; padding: 5px; border-radius: 5px; border: 1px solid #ccc;">
        <script>
            document.getElementById("capitalInput").addEventListener("input", function(e) {
                let value = e.target.value.replace(/[^0-9.]/g, "").replace(/,/g, "");
                if (value) {
                    let parts = value.split(".");
                    parts[0] = parseInt(parts[0]).toLocaleString("en-US");
                    e.target.value = "$" + parts.join(".");
                }
            });
        </script>
        """
        components.html(capital_html, height=50)

    with col2:
        tipo = st.selectbox('Tasa nominal (%):', ['mensual', 'quincenal', 'semanal', 'otra tasa'])
        if tipo == 'mensual':
            TNM = 18
        elif tipo == 'quincenal':
            TNM = 14
        elif tipo == 'semanal':
            TNM = 6.5
        else:
            TNM = st.number_input("Tasa nominal mensual (%):", min_value=1.0, step=0.01, format="%.2f")

        if tipo in ['mensual', 'quincenal', 'semanal']:
            st.write(f"Tasa nominal (%): {TNM}")

        tasa_decimal = TNM / 100

        # **IMPORTANTE:** Aquí necesitarás convertir el valor del campo `capitalInput` a número para los cálculos.
        # Puedes hacerlo con un `st.text_input` oculto o usar otro método para capturarlo en Python.

        cuota_pura = 0  # ← Deberías calcular esto después de obtener `capital`
        iva = cuota_pura * IVA
        interes = 0  # ← Depende de `capital`
        amortizacion = cuota_pura - interes

        monto = 0.0
        if st.checkbox('Calcular monto por cuota'):
            monto_final = interes + amortizacion + iva
            if cantidad_cuotas == 1:
                monto_final, redondeo = redondear_mil_condicional(monto_final)
            elif cantidad_cuotas == 2:
                monto_final, redondeo = redondear_mil_condicional(monto_final / 2)
            else:
                monto_final, redondeo = redondear_mil_condicional(interes + amortizacion + iva)
            redondeo = math.trunc(redondeo)
            st.write(f'Monto Fijo por Cuota: ${monto_final:,.2f}, Redondeo: ${redondeo:,.2f}')
        else:
            st.markdown("#### Monto Fijo por Cuota:")
            monto_html = """
            <input type="text" id="montoInput" placeholder="$0.00" style="width: 100%; font-size: 20px; text-align: right; padding: 5px; border-radius: 5px; border: 1px solid #ccc;">
            <script>
                document.getElementById("montoInput").addEventListener("input", function(e) {
                    let value = e.target.value.replace(/[^0-9.]/g, "").replace(/,/g, "");
                    if (value) {
                        let parts = value.split(".");
                        parts[0] = parseInt(parts[0]).toLocaleString("en-US");
                        e.target.value = "$" + parts.join(".");
                    }
                });
            </script>
            """
            components.html(monto_html, height=50)

crear()