import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd

# Ocultar el botón de Deploy con CSS
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

def authenticate():
    """Autentica con Google Sheets y guarda el cliente en la sesión."""
    if "gspread_client" not in st.session_state:
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
        st.session_state["gspread_client"] = gspread.authorize(creds)

def get_worksheet(sheet_id):
    """Obtiene la hoja de cálculo reutilizando la autenticación."""
    authenticate()  # Asegura que `st.session_state["gspread_client"]` está disponible
    client = st.session_state["gspread_client"]
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.worksheet("Sheet1")

def overwrite_sheet(new_data, sheet_id):
    """
    Sobrescribe toda la hoja de cálculo con los nuevos datos.
    
    :param new_data: Lista de listas, donde cada sublista representa una fila.
    :param sheet_id: ID de la hoja de cálculo en Google Sheets.
    """
    worksheet = get_worksheet(sheet_id)
    worksheet.clear()  # Borra todo el contenido de la hoja
    worksheet.update("A1", new_data)  # Escribe los nuevos datos desde A1


def delete_data(id_value, sheet_id, column_index=1):
    """Elimina todas las filas donde id_value esté presente en la columna especificada."""
    worksheet = get_worksheet(sheet_id)
    
    try:
        cells = worksheet.findall(str(id_value), in_column=column_index)  # Busca en una columna específica
        if not cells:
            return f"ID {id_value} no encontrado en la columna {column_index}."
        
        row_indices = sorted(set(cell.row for cell in cells), reverse=True)
        for row in row_indices:
            worksheet.delete_rows(row)
        
        return f"Se eliminaron {len(row_indices)} fila(s) con ID {id_value}."
    
    except Exception as e:
        return f"Error al eliminar datos: {e}"




def save_data(id_value, column_name, new_value, sheet_id):
    worksheet = get_worksheet(sheet_id)
    col_labels = worksheet.row_values(1)
    if column_name not in col_labels:
        st.error("...")
        return
    col_index = col_labels.index(column_name) + 1
    cell = worksheet.find(str(id_value))
    if cell:
        worksheet.update_cell(cell.row, col_index, new_value)

def append_data(new_values, sheet_id):
    worksheet = get_worksheet(sheet_id)
    worksheet.append_row(new_values)

def load_data(url):
    return pd.read_excel(url,engine='openpyxl')

def load_data_vendedores(url):
    df=pd.read_excel(url,engine='openpyxl')
    if st.session_state['user_data']['permisos'].iloc[0]!='admin':
        df=df[df['vendedor']==st.session_state['usuario']]
    return df
def load_data1(url):
    return pd.read_csv(url)

def delete(index):#borra una fila completa y acomoda el resto de la hoja para que no quede el espacio en blanco
    delete_data(index,st.secrets['ids']['clientes'])
def save(id,column,data):#modifica un solo dato
    save_data(id,column,data,st.secrets['ids']['clientes'])
def new(data):#añade una columna entera de datos
    append_data(data,st.secrets['ids']['clientes'])




st.session_state['usuarios']=load_data1(st.secrets['urls']['usuarios'])



# Validación simple de usuario y clave con un archivo CSV
def validarUsuario(usuario, clave):
    st.session_state['usuarios']=load_data1(st.secrets['urls']['usuarios'])
    """
    Permite la validación de usuario y clave.
    :param usuario: Usuario ingresado
    :param clave: Clave ingresada
    :return: True si el usuario y clave son válidos, False en caso contrario
    """
    try:
        dfusuarios = st.session_state['usuarios']  # Carga el archivo CSV
        # Verifica si existe un usuario y clave que coincidan
        if len(dfusuarios[(dfusuarios['usuario'] == usuario) & (dfusuarios['clave'] == clave)]) > 0:
            return True
    except FileNotFoundError:
        st.error("El archivo 'usuarios.csv' no se encontró.")
    except Exception as e:
        st.error(f"Error al validar usuario: {e}")
    return False

def generarMenu(usuario,permiso):
    st.session_state['usuarios']=load_data1(st.secrets['urls']['usuarios'])
    """
    Genera el menú en la barra lateral dependiendo del usuario.
    :param usuario: Usuario autenticado
    """
    with st.sidebar:
        try:
            dfusuarios = st.session_state['usuarios']
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
                st.page_link("pages/parametros.py", label="Parámetros", icon=":material/group:")

            # Reportes
            st.subheader("Reportes")
            if permiso!='admin':
                st.page_link('pages/repo_morosos.py', label="Reporte Morosos", icon=":material/group:")
            else:
                st.page_link('pages/repo_comision.py', label="Reporte Comisiones", icon=":material/group:")
                st.page_link('pages/repo_morosos.py', label="Reporte Morosos", icon=":material/group:")
                st.page_link('pages/reporte_general.py', label="Reporte General", icon=":material/group:")
            st.subheader("Otros")
            st.page_link('pages/preliminar.py', label="Actualizaciones preliminares", icon=":material/group:")

            # Botón de cierre de sesión
            if st.button("Salir"):
                del st.session_state['usuario']
                st.switch_page('inicio.py')
                

        except FileNotFoundError:
            st.error("El archivo 'usuarios.csv' no se encontró.")
        except Exception as e:
            st.error(f"Error al generar el menú: {e}")
def guardar_log():
    pass

def generarLogin():
    # Ocultar el menú y el pie de página de Streamlit
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.session_state['usuarios'] = load_data1(st.secrets['urls']['usuarios'])
    usuarios = st.session_state['usuarios']

    if 'usuario' in st.session_state:
        generarMenu(st.session_state['usuario'], st.session_state['user_data']['permisos'].iloc[0])
    else:
        try:
            with st.form('frmLogin'):
                parUsuario = st.text_input('Usuario')
                parPassword = st.text_input('Password', type='password')
                if st.form_submit_button('Ingresar'):
                    if validarUsuario(parUsuario, parPassword):
                        st.session_state['usuario'] = parUsuario
                        usuario = usuarios[usuarios['usuario'] == st.session_state['usuario']]
                        st.session_state['user_data'] = usuario
                        guardar_log()  # Registrar el inicio de sesión en logs
                        st.rerun()  # Recargar la aplicación inmediatamente después del login exitoso
                    else:
                        st.error("Usuario o clave inválidos")
        except:
            st.switch_page('inicio.py')


from datetime import datetime

def historial(old_values, new_values):
    """
    Registra en una hoja de Google Sheets un cambio en los datos.

    :param old_values: Lista con los valores anteriores.
    :param new_values: Lista con los valores nuevos.
    """
    worksheet = get_worksheet(st.secrets['ids']['historial'])

    # Obtener la cantidad de filas actuales para generar el índice numérico
    existing_data = worksheet.get_all_values()
    index = len(existing_data)  # Nueva fila será una más que las actuales

    # Obtener la fecha y hora actual
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Obtener el usuario actual
    usuario = st.session_state.get("usuario", "Desconocido")

    # Crear las filas con la estructura: [Fecha, Usuario, Índice, Valores...]
    row_old = [timestamp, usuario, index] + old_values
    row_new = [timestamp, usuario, index + 1] + new_values

    # Agregar ambas filas a la hoja
    worksheet.append_row(row_old)
    worksheet.append_row(row_new)
def display_cobranzas():
    pass