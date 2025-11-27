import streamlit as st
import pandas as pd

st.title("Verificación OneDrive Personal – CSV delimitado por ;")

url = "https://onedrive.live.com/download?resid=3EBA015078183D6B!140&authkey=!CJl6TtkeBYTKNX"

try:
    df = pd.read_csv(url, sep=';', engine='python')
    st.success("✅ Archivo leído correctamente con sep=';'")
    st.dataframe(df.head())

except Exception as e:
    st.error("❌ No se pudo leer el archivo ni con sep=';'")
    st.code(str(e))

