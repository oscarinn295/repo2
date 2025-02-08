import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# Definir los alcances de la API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Cargar credenciales desde secrets.toml
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)

# Autenticación con gspread
client = gspread.authorize(creds)

# ID de la hoja de cálculo
sheet_id = "1N0KdT_rPYM3hoVf8dfT1l06On24rUPnQhnyVPiU3wMA"
workbook = client.open_by_key(sheet_id)

# Datos a insertar
values = [
    ["Name", "Price", "Quantity"],
    ["Basketball", 29.99, 1],
    ["Jeans", 39.99, 4],
    ["Soap", 7.99, 3],
]

# Obtener lista de hojas existentes
worksheet_list = [ws.title for ws in workbook.worksheets()]
new_worksheet_name = "Values"

# Verificar si la hoja existe o crear una nueva
if new_worksheet_name in worksheet_list:
    sheet = workbook.worksheet(new_worksheet_name)
else:
    sheet = workbook.add_worksheet(new_worksheet_name, rows=10, cols=10)

# Limpiar y actualizar la hoja
sheet.clear()
sheet.update(f"A1:C{len(values)}", values)

# Agregar fórmulas para sumar precios y cantidades
sheet.update_cell(len(values) + 1, 2, "=SUM(B2:B4)")
sheet.update_cell(len(values) + 1, 3, "=SUM(C2:C4)")

# Formatear encabezados en negrita
sheet.format("A1:C1", {"textFormat": {"bold": True}})

st.success("Datos actualizados en Google Sheets")
