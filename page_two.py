import streamlit as st
import pandas as pd
from io import BytesIO

def unir_excels():
    # Explicación de los pasos
    st.markdown(
        """
        ### **Unificación de Múltiples Archivos Excel** 📄📚
        1. Suba varios archivos Excel. Todos deben tener las **mismas columnas**.
        2. Los archivos se unificarán en un solo DataFrame.
        3. Una vez unificados, podrá previsualizar los datos y descargarlos como un único archivo Excel. 📥✨
        """
    )

    # Opción para subir múltiples archivos
    uploaded_files = st.file_uploader("Subir múltiples archivos Excel", type=["xlsx"], accept_multiple_files=True)

    if uploaded_files:
        try:
            # Leer y concatenar los archivos
            dataframes = [pd.read_excel(file) for file in uploaded_files]
            df_concatenado = pd.concat(dataframes, ignore_index=True)

            # Mostrar el DataFrame unificado
            st.write("Vista previa del archivo unificado:")
            st.dataframe(df_concatenado)

            # Guardar el DataFrame unificado en un archivo descargable
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_concatenado.to_excel(writer, index=False, sheet_name="Unificado")

            # Botón de descarga
            st.download_button(
                label="Descargar archivo unificado",
                data=buffer.getvalue(),
                file_name="archivo_unificado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Error al procesar los archivos: {e}")
