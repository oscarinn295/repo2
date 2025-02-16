import streamlit as st
import login
import pandas as pd
if st.button("Volver"):
    st.session_state['cliente'] = None
    st.switch_page("pages/clientes.py")
# Verificar si 'cliente' está en session_state
if 'cliente' not in st.session_state :
    st.error("No se ha seleccionado ningún cliente.")
else:
    cliente = st.session_state['cliente']

    # Cargar los datos de préstamos y cobranzas
    prestamos = login.load_data(st.secrets['urls']['prestamos'])
    cobranzas = login.load_data(st.secrets['urls']['cobranzas'])

    # Filtrar préstamos y cobranzas por el cliente seleccionado
    prestamos_cliente = prestamos[prestamos['nombre'] == cliente['nombre']]
    cobranzas_cliente = cobranzas[cobranzas['nombre'] == cliente['nombre']]

    cobranzas_cliente['vencimiento'] = pd.to_datetime(cobranzas_cliente['vencimiento'], format='%d-%m-%Y', errors='coerce')
    prestamos_cliente['fecha'] = pd.to_datetime(prestamos_cliente['fecha'], format='%d-%m-%Y', errors='coerce')


    # Obtener la fecha mínima y máxima de vencimiento, manejando NaT
    primer_cobranza = cobranzas_cliente['vencimiento'].min()
    ultima_cobranza = cobranzas_cliente['vencimiento'].max()

    primer_prestamo = prestamos_cliente['fecha'].min()
    ultimo_prestamo = prestamos_cliente['fecha'].max()

    # Verificar si los valores son NaT antes de aplicar strftime
    primer_cobranza = primer_cobranza.strftime('%d-%m-%Y') if pd.notna(primer_cobranza) else ""
    ultima_cobranza = ultima_cobranza.strftime('%d-%m-%Y') if pd.notna(ultima_cobranza) else ""

    primer_prestamo = primer_prestamo.strftime('%d-%m-%Y') if pd.notna(primer_prestamo) else ""
    ultimo_prestamo = ultimo_prestamo.strftime('%d-%m-%Y') if pd.notna(ultimo_prestamo) else ""

    col1,col2,col3,col4=st.columns(4)
    with col1:
        #primer y ultima cobranza
        st.write(f"primer vencimiento: {primer_cobranza}")
        st.write(f"ultimo vencimiento: {ultima_cobranza}")
        #primer y ultimo prestamo
        st.write(f"primer prestamo: {primer_prestamo}")
        st.write(f"ultimo prestamo: {ultimo_prestamo}")
        
    with col2:
        #capital entregado
        entregado=prestamos_cliente['capital'].sum()
        st.write(f"capital entregado: {entregado}")
        #total de intereses
        mora=cobranzas_cliente['mora'].sum()
        st.write(f"total de intereses: {mora}")
        
    with col3:
        #total de deuda
        monto_mora=cobranzas_cliente['monto_recalculado_mora'].sum()-cobranzas_cliente['pago'].sum()
        st.write(f"total adeudado: {monto_mora}")

        #total pagado
        pagado=cobranzas_cliente['pago'].sum()
        st.write(f"total pagado: {pagado}")

    # Función para mostrar el nivel de morosidad
    def nivel_de_morosidad():
        with st.container():
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader('Pagados')
                pagados = cobranzas_cliente[cobranzas_cliente['estado'] == 'pago total']
                if pagados.empty:
                    st.write("No hay pagos registrados.")
                else:
                    st.dataframe(pagados, use_container_width=True)

            with col2:
                st.subheader('Atrasados')
                atrasados = cobranzas_cliente[cobranzas_cliente['estado'] == 'en mora']
                if atrasados.empty:
                    st.write("No hay pagos atrasados.")
                else:
                    st.dataframe(atrasados, use_container_width=True)

            with col3:
                st.subheader('Pendientes')
                pendientes = cobranzas_cliente[cobranzas_cliente['estado'] == 'pendiente de pago']
                if pendientes.empty:
                    st.write("No hay pagos pendientes.")
                else:
                    st.dataframe(pendientes, use_container_width=True)

    # Función para mostrar préstamos y cobranzas relacionadas
    def cartones():
        if prestamos_cliente.empty:
            st.warning("Este cliente no tiene préstamos registrados.")
            return

        for _, row in prestamos_cliente.iterrows():
            st.markdown(f"### Préstamo ID: {row['id']}")
            st.write(f"📅 **Fecha:** {row['fecha']}")
            st.write(f"💰 **Capital:** {row['capital']}")
            st.write(f"📌 **Cantidad de cuotas:** {row['cantidad']}")
            st.write(f"📆 **Vencimiento:** {row['vence']}")
            st.write(f"📝 **Estado:** {row['estado']}")
            
            # Filtrar cobranzas relacionadas con este préstamo
            cobranzas_prestamo = cobranzas_cliente[cobranzas_cliente['prestamo_id'] == row['id']]

            if cobranzas_prestamo.empty:
                st.info("No hay cobranzas registradas para este préstamo.")
            else:
                st.dataframe(cobranzas_prestamo, use_container_width=True)
    # Mostrar información
    nivel_de_morosidad()
    cartones()
