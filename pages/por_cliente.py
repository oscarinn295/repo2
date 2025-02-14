import streamlit as st
import login
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
