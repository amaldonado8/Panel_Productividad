import streamlit as st
import pandas as pd
import csv

st.set_page_config(page_title="Diagnóstico de Datos", layout="wide")

# =========================================================
# Función robusta para cargar CSV y limpiar columnas
# =========================================================
def load_csv(path):
    try:
        # Detectar separador
        with open(path, "r", encoding="latin-1") as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            sep = dialect.delimiter
    except:
        sep = ";"

    df = pd.read_csv(path, sep=sep, encoding="latin-1", dtype=str)

    # Normalizar columnas
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "")
        .str.replace("\ufeff", "", regex=False)
        .str.replace("﻿", "", regex=False)
    )

    return df


# =========================================================
# Cargar archivos
# =========================================================
st.title("🔍 Diagnóstico de Columnas en CSVs")

st.markdown("### 1️⃣ Leyendo Gestion_part1.csv...")
df = load_csv("Data/Gestion_part1.csv")
st.write("Columnas detectadas:", list(df.columns))


st.markdown("### 2️⃣ Leyendo TipoContacto.csv...")
tipo_contacto = load_csv("Data/TipoContacto.csv")
st.write("Columnas detectadas:", list(tipo_contacto.columns))


st.markdown("### 3️⃣ Leyendo Producto.csv...")
producto = load_csv("Data/Producto.csv")
st.write("Columnas detectadas:", list(producto.columns))


st.markdown("### 4️⃣ Leyendo Orden etapa.csv...")
orden_etapa = load_csv("Data/Orden etapa.csv")
st.write("Columnas detectadas:", list(orden_etapa.columns))


st.markdown("### 5️⃣ Leyendo Semana.csv...")
semana = load_csv("Data/Semana.csv")
st.write("Columnas detectadas:", list(semana.columns))


st.warning("📌 Copia las 5 listas de arriba y envíamelas aquí. Con eso genero el panel completo sin errores.")
st.stop()


