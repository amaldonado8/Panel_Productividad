import streamlit as st
import pandas as pd

st.title("Verificación de descarga directa OneDrive Personal")

url = "https://onedrive.live.com/download?resid=3EBA015078183D6B!seda49789e0914c58a357b5262902c422&authkey=!CQl6TtkeBYTKNX"

try:
    df = pd.read_csv(url, sep=';', engine='python')
    st.success("✅ Archivo CSV leído correctamente")
    st.write("Dimensiones:", df.shape)
    st.dataframe(df.head())

except Exception as e:
    st.error("❌ Error al leer el archivo")
    st.code(str(e))
