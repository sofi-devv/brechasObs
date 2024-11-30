import streamlit as st
from page_one import calculo_brechas
from page_two import unir_excels  # Importar la nueva página

# Configuración de la app Streamlit con múltiples páginas
st.set_page_config(page_title="Cálculo de Brechas", layout="wide")

# Definición de las páginas
page = st.sidebar.selectbox(
    "Seleccione la página", 
    ["Cálculo de Brechas", "Unificación de Excels"]
)

# Navegación a la página seleccionada
if page == "Cálculo de Brechas":
    calculo_brechas()
elif page == "Unificación de Excels":
    unir_excels()
