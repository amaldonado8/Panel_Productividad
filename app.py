import streamlit as st
import pandas as pd
import csv

st.title("Verificación OneDrive Personal – CSV con limpieza automática")

url = "https://onedrive.live.com/download?resid=3EBA015078183D6B!140&authkey=!CJl6TtkeBYTKNX"

try:
    df = pd.read_csv(
        url,
        sep=None,  
        engine="python",
        on_bad_lines="skip",  
        quoting=csv.QUOTE_NONE,
        encoding="latin1"   # tolerante a caracteres raros
    )
    
    st.success("✅ Archivo leído correctamente con limpieza automática")
    st.write("Forma:", df.shape)
    st.dataframe(df.head())

except Exception as e:
    st.error("❌ No se pudo leer el archivo")
    st.code(str(e))
