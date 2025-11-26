import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Panel Productividad BS", layout="wide")

# -------------------------
# Cargar datos
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Data/gestiones.csv", encoding="latin-1")
    return df

df = load_data()

# -------------------------
# FILTROS SUPERIORES
# -------------------------
st.markdown("### 🔎 Filtros")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    fecha = st.selectbox("Fecha Gestión", ["Todas"] + sorted(df["FechaGestion"].unique().tolist()))

with col2:
    supervisor = st.selectbox("Supervisor", ["Todas"] + sorted(df["Supervisor"].unique().tolist()))

with col3:
    gestor = st.selectbox("Gestor", ["Todas"] + sorted(df["Gestor"].unique().tolist()))

with col4:
    etapa = st.selectbox("Etapa", ["Todas"] + sorted(df["Etapa"].unique().tolist()))

with col5:
    estrategia = st.selectbox("Estrategia", ["Todas"] + sorted(df["Estrategia"].unique().tolist()))

with col6:
    tipo = st.selectbox("Tipo", ["Todas"] + sorted(df["Tipo"].unique().tolist()))

# Aplicar filtros
df_filtered = df.copy()

if fecha != "Todas":
    df_filtered = df_filtered[df_filtered["FechaGestion"] == fecha]
if supervisor != "Todas":
    df_filtered = df_filtered[df_filtered["Supervisor"] == supervisor]
if gestor != "Todas":
    df_filtered = df_filtered[df_filtered["Gestor"] == gestor]
if etapa != "Todas":
    df_filtered = df_filtered[df_filtered["Etapa"] == etapa]
if estrategia != "Todas":
    df_filtered = df_filtered[df_filtered["Estrategia"] == estrategia]
if tipo != "Todas":
    df_filtered = df_filtered[df_filtered["Tipo"] == tipo]

# -------------------------
# TARJETAS DE MÉTRICAS
# -------------------------
st.markdown("---")

colA, colB, colC, colD, colE = st.columns(5)

with colA:
    st.metric("Gestiones", f"{df_filtered['Gestiones'].sum():,.0f}")

with colB:
    st.metric("Número Operaciones", f"{df_filtered['NumeroOperaciones'].sum():,.0f}")

with colC:
    st.metric("Contacto", f"{df_filtered['Contacto'].sum():,.0f}")

with colD:
    st.metric("Contacto Directo", f"{df_filtered['ContactoDirecto'].sum():,.0f}")

with colE:
    st.metric("Compromisos", f"{df_filtered['Compromisos'].sum():,.0f}")

# -------------------------
# ANILLO DE TIPO CONTACTO
# -------------------------
st.markdown("### 📞 Tipo de Contacto")

contacto_counts = df_filtered["TipoContacto"].value_counts().reset_index()
contacto_counts.columns = ["TipoContacto", "Cantidad"]

fig_pie = px.pie(
    contacto_counts,
    values="Cantidad",
    names="TipoContacto",
    hole=0.6,
    color_discrete_sequence=px.colors.sequential.Blues
)

col_pie, col_vacio = st.columns([2, 1])
with col_pie:
    st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------
# HORA DE LA PRIMERA GESTIÓN
# -------------------------
st.markdown("### 🕒 Hora de la primera gestión")

df_hora = df_filtered.groupby("Gestor")["HoraGestion"].min().reset_index()
df_hora = df_hora.sort_values("HoraGestion")

st.dataframe(df_hora, use_container_width=True)

# -------------------------
# GESTIONES POR HORA (SLIDER)
# -------------------------
st.markdown("### ⏳ Gestiones por Hora")

hora_min = int(df_filtered["Hora"].min())
hora_max = int(df_filtered["Hora"].max())

h1, h2 = st.columns([1,1])

with h1:
    hora_inicio = st.slider("Hora desde:", min_value=hora_min, max_value=hora_max, value=hora_min)

with h2:
    hora_fin = st.slider("Hora hasta:", min_value=hora_min, max_value=hora_max, value=hora_max)

df_horas = df_filtered[(df_filtered["Hora"] >= hora_inicio) & (df_filtered["Hora"] <= hora_fin)]

tabla_horas = df_horas.pivot_table(
    index="Gestor",
    columns="Hora",
    values="Gestiones",
    aggfunc="sum",
    fill_value=0
)

st.dataframe(tabla_horas, use_container_width=True)

# -------------------------
# TABLA GENERAL POR GESTOR
# -------------------------
st.markdown("### 📋 Resumen por Gestor")

tabla_gen = df_filtered.groupby("Gestor").agg({
    "Gestiones": "sum",
    "CD": "sum",
    "Compromisos": "sum",
    "ContactoDirecto": "sum"
}).reset_index()

tabla_gen["% Contacto Directo"] = tabla_gen["ContactoDirecto"] / tabla_gen["Gestiones"] * 100

st.dataframe(tabla_gen, use_container_width=True)
