import streamlit as st
import pandas as pd

st.title("Verificación de acceso a OneDrive")

# Enlace OneDrive con download=1
url = "https://sicec-my.sharepoint.com/:x:/g/personal/amaldonado_sicobra_com/IQBQ5nuzo3MgSKUAkPeHhAvJARLribJNnL2KGmKGdHYlc4c?download=1"

st.write("Probando acceso al archivo...")

try:
    df = pd.read_csv(url)
    st.success("✅ Archivo leído correctamente")
    st.write("Primeras filas del archivo:")
    st.dataframe(df.head())
except Exception as e:
    st.error("❌ No se pudo leer el archivo")
    st.write("Detalle del error:")
    st.code(e)


