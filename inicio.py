import streamlit as st
import login
st.title("Pagina administrativa de GrupoGon!")
login.generarLogin()
st.text("Esto es una demo de la nueva página de gestión de clientes y algunos datos financieros.")
st.text("Acá ya está replicada toda la información de la vieja página, excepto de los morosos.")
st.text("Hecho por Oscar Molinas.")