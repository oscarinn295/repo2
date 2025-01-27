import streamlit as st
import pandas as pd

# Ocultar el botón de Deploy con CSS
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Validación simple de usuario y clave con un archivo CSV
def validarUsuario(usuario, clave):
    """
    Permite la validación de usuario y clave.
    :param usuario: Usuario ingresado
    :param clave: Clave ingresada
    :return: True si el usuario y clave son válidos, False en caso contrario
    """
    try:
        dfusuarios = pd.read_csv('C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\DB\\usuarios.csv')  # Carga el archivo CSV
        # Verifica si existe un usuario y clave que coincidan
        if len(dfusuarios[(dfusuarios['usuario'] == usuario) & (dfusuarios['clave'] == clave)]) > 0:
            return True
    except FileNotFoundError:
        st.error("El archivo 'usuarios.csv' no se encontró.")
    except Exception as e:
        st.error(f"Error al validar usuario: {e}")
    return False

def generarMenu(usuario):
    """
    Genera el menú en la barra lateral dependiendo del usuario.
    :param usuario: Usuario autenticado
    """
    with st.sidebar:
        try:
            dfusuarios = pd.read_csv('C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\DB\\usuarios.csv')
            dfUsuario = dfusuarios[dfusuarios['usuario'] == usuario]
            nombre = dfUsuario['nombre'].values[0]

            # Bienvenida al usuario
            st.write(f"### Bienvenido/a, **{nombre}**")
            st.page_link("inicio.py", label="Inicio", icon=":material/home:")
            st.divider()

            # Menú principal
            st.subheader("Préstamos")
            st.page_link("pages/clientes.py", label="Clientes", icon=":material/sell:")
            st.page_link("pages/prestamos.py", label="Préstamos", icon=":material/sell:")
            st.page_link("pages/simulador_creditos.py", label="Simulador Créditos", icon=":material/sell:")
            st.page_link("pages/cobranzas.py", label="Cobranzas", icon=":material/sell:")

            # Administración
            st.subheader("Administración")
            st.page_link("pages/movimientos_caja.py", label="Movimientos de Caja", icon=":material/sell:")
            st.page_link("pages/parametros.py", label="Parámetros", icon=":material/group:")

            # Reportes
            st.subheader("Reportes")
            st.page_link('C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\pages\\repo_comision.py', label="Reporte Comisiones", icon=":material/group:")
            st.page_link('C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\pages\\repo_mensual.py', label="Reporte Mensual", icon=":material/group:")
            st.page_link('C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\pages\\repo_morosos.py', label="Reporte Morosos", icon=":material/group:")
            st.page_link('C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\pages\\repo_pagos_cobranzas.py', label="Reporte Cobranzas", icon=":material/group:")
            st.page_link('C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\pages\\repo_ventas.py', label="Reporte de Ventas por Vendedor", icon=":material/group:")
            st.page_link('C:\\Users\\oscar\\Desktop\\laburo\\cobranzas\\streamlitLogin\\pages\\visitas.py', label="Reporte de Visitas", icon=":material/group:")

            # Botón de cierre de sesión
            if st.button("Salir"):
                st.session_state.clear()

        except FileNotFoundError:
            st.error("El archivo 'usuarios.csv' no se encontró.")
        except Exception as e:
            st.error(f"Error al generar el menú: {e}")

def generarLogin():
    """
    Genera la ventana de login o muestra el menú si el login es válido.
    """
    if 'usuario' in st.session_state:
        generarMenu(st.session_state['usuario'])  # Muestra el menú si ya está autenticado
    else:
        with st.form('frmLogin'):
            parUsuario = st.text_input('Usuario')
            parPassword = st.text_input('Password', type='password')
            if st.form_submit_button('Ingresar'):
                if validarUsuario(parUsuario, parPassword):
                    st.session_state['usuario'] = parUsuario
                    st.rerun()  # Forzar redirección para aplicar cambios de estado
                else:
                    st.error("Usuario o clave inválidos")
