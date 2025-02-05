import requests
import json
import streamlit as st
import pandas as pd


# Cargar valores desde secrets.toml
api = st.secrets["api"]['dfs']
url=st.secrets['urls']['usuarios']
idc=st.secrets['ids']['usuarios']
def load_data(URL):
    return pd.read_excel(URL)

def load_data1(URL):
    return pd.read_csv(URL)


def append_data(data:list,ID):
    # Datos a insertar
    payload = {
        "fileId":ID,
        "values": [data]
    }

    requests.post(api, data=json.dumps(payload))

def save_data(id: str, datos):
    """
    Sobrescribe toda la hoja con nuevos datos.
    """
    values = datos.values.tolist()
    values.insert(0, datos.columns.tolist())  # Agrega encabezados

    payload = {
        "fileId": id,
        "values": values,
        "all": True  # Sobrescribir toda la hoja
    }
    requests.post(api, data=json.dumps(payload, default=str))

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
        dfusuarios = load_data1(url)  # Carga el archivo CSV
        # Verifica si existe un usuario y clave que coincidan
        if len(dfusuarios[(dfusuarios['usuario'] == usuario) & (dfusuarios['clave'] == clave)]) > 0:
            return True
    except FileNotFoundError:
        st.error("El archivo 'usuarios.csv' no se encontró.")
    except Exception as e:
        st.error(f"Error al validar usuario: {e}")
    return False

def generarMenu(usuario,permiso):
    """
    Genera el menú en la barra lateral dependiendo del usuario.
    :param usuario: Usuario autenticado
    """
    with st.sidebar:
        try:
            dfusuarios = load_data1(url)
            dfUsuario = dfusuarios[dfusuarios['usuario'] == usuario]
            nombre = dfUsuario['nombre'].iloc[0]

            # Bienvenida al usuario
            st.write(f"### Bienvenido/a, **{nombre}**")
            st.page_link("inicio.py", label="Inicio", icon=":material/home:")
            st.divider()

            # Menú principal
            st.subheader("Préstamos")
            st.page_link("pages/clientes.py", label="Clientes", icon=":material/sell:")
            st.page_link("pages/cobranzas.py", label="Cobranzas", icon=":material/sell:")
            st.page_link("pages/prestamos.py", label="Préstamos", icon=":material/sell:")
            st.page_link("pages/simulador_creditos.py", label="Simulador Créditos", icon=":material/sell:")

            # Administración
            if permiso=='admin':
                st.subheader("Administración")
                st.page_link("pages/movimientos_caja.py", label="Movimientos de Caja", icon=":material/sell:")
                st.page_link("pages/parametros.py", label="Parámetros", icon=":material/group:")

            # Reportes
            st.subheader("Reportes")
            if permiso!='admin':
                st.page_link('pages/repo_morosos.py', label="Reporte Morosos", icon=":material/group:")
            else:
                st.page_link('pages/repo_comision.py', label="Reporte Comisiones", icon=":material/group:")
                st.page_link('pages/repo_mensual.py', label="Reporte Mensual", icon=":material/group:")
                st.page_link('pages/repo_morosos.py', label="Reporte Morosos", icon=":material/group:")
                st.page_link('pages/repo_cobranzas.py', label="Reporte Cobranzas", icon=":material/group:")
                st.page_link('pages/repo_ventas.py', label="Reporte de Ventas por Vendedor", icon=":material/group:")
            # Botón de cierre de sesión
            if st.button("Salir"):
                del st.session_state['usuario']
                st.switch_page('inicio.py')
                

        except FileNotFoundError:
            st.error("El archivo 'usuarios.csv' no se encontró.")
        except Exception as e:
            st.error(f"Error al generar el menú: {e}")
def guardar_log_usuario():
    """
    Guarda en Google Sheets la fecha, hora y usuario que inició sesión.
    """
    if 'usuario' in st.session_state:
        usuario = st.session_state['usuario']
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora actual

        payload = {
            "fileId": st.secrets['ids']['logs'],  # ID de la hoja de logs
            "values": [[fecha_hora, usuario]]  # Datos a registrar
        }
        response = requests.post(api, data=json.dumps(payload))

        return response.json()

    return {"status": "error", "message": "No hay usuario en sesión"}

def generarLogin():
    usuarios=load_data1(st.secrets['urls']['usuarios'])
    """
    Genera la ventana de login o muestra el menú si el login es válido.
    """
    if 'usuario' in st.session_state:
        generarMenu(st.session_state['usuario'],st.session_state['user_data']['permisos'].iloc[0])  # Muestra el menú si ya está autenticado
    else:
        with st.form('frmLogin'):
            parUsuario = st.text_input('Usuario')
            parPassword = st.text_input('Password', type='password')
            if st.form_submit_button('Ingresar'):
                if validarUsuario(parUsuario, parPassword):
                    st.session_state['usuario'] = parUsuario
                    
                    usuario=usuarios[usuarios['usuario']==st.session_state['usuario']]
                    st.session_state['user_data']=usuario

                    guardar_log_usuario()  # Registrar el inicio de sesión en logs
                else:
                    st.error("Usuario o clave inválidos")
                    st.switch_page('inicio.py')


from datetime import datetime

def historial( datos: pd.Series,tipo_movimiento: str):
    usuario=st.session_state['usuario']
    """
    Guarda una serie de pandas en el historial de Google Sheets.
    
    :param usuario: Nombre del usuario que realiza la acción
    :param tipo_movimiento: Tipo de movimiento registrado
    :param datos: Serie de Pandas con los datos a guardar
    """
    # Obtener la fecha y hora actual
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Convertir la serie a lista de valores
    valores = datos.tolist()
    
    # Crear la fila con la estructura deseada
    fila = [fecha_hora, usuario, tipo_movimiento] + valores
    
    # Cargar configuración de la API y el ID de la hoja de historial
    api = st.secrets["api"]["dfs"]
    historial_id = st.secrets["ids"]["historial"]
    
    # Crear el payload para la API
    payload = {
        "fileId": historial_id,
        "values": [fila]  # Convertir la fila en lista de listas
    }
    
    # Enviar la solicitud a la API
    response = requests.post(api, data=json.dumps(payload))
    
    return response.json()