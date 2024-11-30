# pip install --upgrade streamlit

# python -m streamlit run app.py


import streamlit as st
import pandas as pd
from io import BytesIO
from difflib import SequenceMatcher
# openpyxl es necesario para la exportación a Excel

# Lista base de valores permitidos
BASE_VALUES = [
    'Bogotá D.C', 'Cundinamarca', 'Boyacá', 'Caldas', 'Atlántico',
    'Risaralda', 'Quindío', 'Antioquia', 'Valle', 'Huila', 'Santander',
    'Tolima', 'Casanare', 'La Guajira', 'Meta', 'Cauca', 'Cesar',
    'Sucre', 'San Andrés', 'Magdalena', 'Norte de Santander',
    'Bolívar', 'Córdoba', 'Nariño', 'Caquetá', 'Arauca', 'Putumayo',
    'Vichada', 'Guaviare', 'Chocó', 'Amazonas', 'Guainía', 'Vaupés',
    'Manizales', 'Tunja', 'Medellín', 'Armenia', 'Pereira',
    'Bucaramanga', 'Neiva', 'Cali', 'Cartagena', 'Ibagué', 'Quibdó',
    'Pasto', 'Villavicencio', 'Popayán', 'Barranquilla', 'Florencia',
    'Santa Marta', 'Riohacha', 'Valledupar', 'Cúcuta', 'Montería',
    'Sincelejo', 'Valle del Cauca', 'Leticia', 'San José del Guaviare',
    'Yopal', 'Mitú', 'Inírida', 'Puerto Carreño', 'Mocoa'
]

# Lista de índices para calcular respecto al máximo
indices_maximo = [5, 6, 7, 8, 9, 10, 21]

# Función para verificar la consistencia de valores en la columna
def verificar_consistencia(columna, base):
    errores = []
    for valor in columna:
        if valor not in base:
            sugerencias = [
                base_value for base_value in base
                if SequenceMatcher(None, valor.lower(), base_value.lower()).ratio() >= 0.8
            ]
            if sugerencias:
                errores.append((valor, sugerencias[0]))  # Usar la primera sugerencia
    return errores

# Función para procesar el DataFrame
def procesar_df(df, nombre):
    df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors='coerce')
    if int(nombre) in indices_maximo:
        referencia = df.iloc[:, 1].max()
        df['Diferencia respecto al referencia'] = round(df.iloc[:, 1] - referencia, 2)
    else:
        referencia = df.iloc[:, 1].min()
        df['Diferencia respecto al referencia'] = round(df.iloc[:, 1] - referencia, 2)
    percentiles = df['Diferencia respecto al referencia'].quantile([0.25, 0.75])
    df['Categoría'] = pd.cut(df['Diferencia respecto al referencia'],
                             bins=[-float('inf'), percentiles[0.25], percentiles[0.75], float('inf')],
                             labels=['Baja', 'Media', 'Alta'])
    df['Puesto'] = df['Diferencia respecto al referencia'].rank(ascending=True, method='min')
    df["Número Indicador"] = nombre
    df.sort_values(['Puesto', 'Categoría'], inplace=True)
    return df

def calculo_brechas():
    st.title("Cálculo de Brechas")

    # Paso 1: Subida de archivo
    st.header("Paso 1: Suba su archivo Excel 📄⬆️")
    st.markdown(
        """
        ### Tenga en cuenta las siguientes recomendaciones:
        1. Cargue un archivo Excel que contenga **dos columnas**:
           - La **primera columna** debe incluir nombres de regiones o departamentos.  
           - La **segunda columna** debe contener valores numéricos que serán procesados. 
        2. **Para el caso de los territorios, se tiene un conjutno de nombres estandarizados para los mismos** por lo que si el sistema detecta nombres similares pero no idénticos (como errores en mayúsculas o tildes), se lo notificaremos para que realice las correcciones necesarias y se garantice la consistencia de la información. ⚠️
        3. Una vez que el archivo sea validado, podrá previsualizar el contenido antes de continuar. 👀✅
        """
    )
    uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            if df.shape[1] < 2:
                st.error("El archivo debe contener al menos dos columnas.")
                return
            df.rename(columns={df.columns[0]: "Territorio", df.columns[1]: "Valor Indicador"}, inplace=True)
            st.write("Vista previa del archivo subido con columnas renombradas:")
            st.dataframe(df)
            columna1 = df["Territorio"].astype(str)
            errores = verificar_consistencia(columna1, BASE_VALUES)
            if errores:
                st.warning("Se encontraron valores inconsistentes:")
                for original, sugerencia in errores:
                    st.write(f"- **{original}** → ¿Quizás quiso decir **{sugerencia}**?")
            else:
                st.success("Todos los valores en la columna 'Territorio' son consistentes.")
            st.write("Archivo cargado correctamente. Avancemos al siguiente paso.")
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
            return

        # Paso 2: Selección de indicador y asociación de columnas
        st.header("Paso 2: Seleccione el indicador correspondiente 🏷️📊")
        st.markdown(
            """
            1. Elija de una lista desplegable el indicador que corresponde a los datos de su archivo. 📋👇
            2. Este indicador incluirá dos valores asociados:
               - **Dimensión**: Se agregará como una nueva columna a su archivo.
               - **Número**: También se agregará como una nueva columna a su archivo.
            3. Antes de descargar su archivo, los datos serán procesados:
               - Calcularemos las diferencias respecto a un valor de referencia (máximo o mínimo, según el indicador).
               - Asignaremos categorías (Alta, Media, Baja) basadas en percentiles.
               - Generaremos rankings y organizaremos los datos para facilitar su análisis. 📈📉
            4. Finalmente, podrá descargar su archivo Excel actualizado y procesado. 📥✨
            """
        )
        try:
            indicadores_file = "data/indicadores.xlsx"
            indicadores_df = pd.read_excel(indicadores_file)
            nombres_unicos = indicadores_df["Nombre"].unique()
            indicador_seleccionado = st.selectbox(
                "Seleccione el indicador para asociarlo a las observaciones:",
                nombres_unicos
            )
            # Selección del año
            st.markdown("### Seleccione el año para las observaciones 📅")
            lista_años = list(range(2023, 2031))  # Lista fija de años del 2023 al 2030
            año_seleccionado = st.selectbox(
                "Seleccione el año asociado al indicador:",
                lista_años
            )
            if indicador_seleccionado:
                dimension_asociada = indicadores_df[indicadores_df["Nombre"] == indicador_seleccionado]["Dimensión"].values[0]
                numero_asociado = indicadores_df[indicadores_df["Nombre"] == indicador_seleccionado]["Número"].values[0]
                df["Nombre"] = indicador_seleccionado
                df["Dimensión"] = dimension_asociada
                df["Año"] = año_seleccionado
                df_procesado = procesar_df(df, numero_asociado)
                st.write("El dataset procesado con las nuevas columnas:")
                st.dataframe(df_procesado)
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_procesado.to_excel(writer, index=False, sheet_name="Datos Procesados")
                st.download_button(
                    label="Descargar archivo procesado",
                    data=buffer.getvalue(),
                    file_name="archivo_procesado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Error al cargar el archivo de indicadores: {e}")

