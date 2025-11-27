import streamlit as st
import pandas as pd

st.title("Verificación de acceso a OneDrive Personal")

url = "https://onedrive.live.com/download?resid=3EBA015078183D6B!140&authkey=!CJl6TtkeBYTKNX"

st.write("Intentando leer el archivo de OneDrive Personal (120 MB)...")

try:
    df = pd.read_csv(url)
    st.success("✅ Archivo leído correctamente desde OneDrive Personal")
    st.write("Primeras filas del archivo:")
    st.dataframe(df.head())

except Exception as e:
    st.error("❌ No se pudo leer el archivo")
    st.write("Detalle del error:")
    st.code(str(e))

