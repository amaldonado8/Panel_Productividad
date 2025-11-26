import streamlit as st
import pandas as pd
import plotly.express as px
import csv

st.set_page_config(page_title="Panel Productividad BS", layout="wide")

# =========================================================
# Función robusta para cargar CSV y limpiar columnas
# =========================================================
def load_csv(path):
    try:
        # Detectar separador automáticamente
        with open(path, "r", encoding="latin-1") as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            sep = dialect.delimiter
    except:
        sep = ";"

    df = pd.read_csv(path, sep=sep, encoding="latin-1")

    # Normalizar columnas (quita espacios, BOM, mayúsc/minúsc)
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
        .str.replace(" ", "")
        .str.replace("﻿", "", regex=False)
    )

    return df


# =========================================================
# CARGA TODO
# =========================================================
@st.cache_data
def load_all():

    df = load_csv("Data/Gestion_part1.csv")
    tipo_contacto = load_csv("Data/TipoContacto.csv")
    producto = load_csv("Data/Producto.csv")
    orden_etapa = load_csv("Data/Orden etapa.csv")
    semana = load_csv("Data/Semana.csv")

    # Confirmar columnas limpias
    # st.write(df.columns)
    # st.write(tipo_contacto.columns)

    # -----------------------------------------
    #   MERGES
    # -----------------------------------------

    # TipoContacto.csv tiene columnas: CodigoTipoContacto, TipoContacto
    df = df.merge(
        tipo_contacto,
        left_on="CodigoTipoContacto",
        right_on="CodigoTipoContacto",
        how="left"
    )

    # Producto.csv tiene ProductoGestion y Producto
    df = df.merge(
        producto[["ProductoGestion", "Producto"]],
        on="ProductoGestion",
        how="left"
    )

    # Orden etapa
    df = df.merge(
        orden_etapa,
        on="Etapa",
        how="left"
    )

    # Semana.csv tiene columna fechaGestion, pero en Gestion_part1 es FechaGestion
    semana = semana.rename(columns={"fechaGestion": "FechaGestion"})
    df = df.merge(
        semana,
        on="FechaGestion",
        how="left"
    )

    # -----------------------------------------
    # Crear métricas internas
    # -----------------------------------------
    df["Gestiones"] = 1
    df["Contacto"] = df["EsContacto"]
    df["ContactoDirecto"] = df["EsContactoDirecto"]
    df["Compromisos"] = df["EsCompromiso"]
    df["CD"] = df["EsContactoDirecto"]

    return df


df = load_all()

st.success("Datos cargados correctamente 🎉")
st.write(df.head())

