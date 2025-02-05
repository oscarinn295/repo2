import streamlit as st
import pytz
import datetime

# JavaScript para detectar la zona horaria del usuario
st.markdown(
    """
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            window.location.search = '?tz=' + encodeURIComponent(timezone);
        });
    </script>
    """,
    unsafe_allow_html=True
)

# Obtener la zona horaria desde la URL
query_params = st.experimental_get_query_params()
user_timezone = query_params.get("tz", ["UTC"])[0]

# Obtener la hora actual en la zona horaria del usuario
tz = pytz.timezone(user_timezone)  # Convertir la zona horaria a un objeto pytz
local_time = datetime.datetime.now(tz)  # Obtener la hora en la zona horaria detectada

st.write(f"Zona horaria detectada: {user_timezone}")
st.write(f"Hora local: {local_time.strftime('%Y-%m-%d %H:%M:%S')}")
