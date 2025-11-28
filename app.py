import streamlit as st
import pandas as pd
import plotly.express as px
import csv

st.set_page_config(page_title="Panel Productividad BS", layout="wide")

# =========================================================
# Función robusta para cargar y limpiar CSVs
# =========================================================
def load_csv(path):
    try:
        with open(path, "r", encoding="latin-1") as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            sep = dialect.delimiter
    except:
        sep = ";"

    df = pd.read_csv(path, sep=sep, encoding="latin-1")

    df.columns = (
        df.columns
        .str.replace("ï»¿", "", regex=False)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )
    return df


# =========================================================
# CARGA PRINCIPAL DE DATOS DESDE Data1/
# =========================================================
@st.cache_data
def load_all():



    # Archivo grande unificado
    df = load_csv("Data1/gestiones_actualizado1.csv")

    # Cargar tablas auxiliares desde Data
    tipo_contacto = load_csv("Data/TipoContacto.csv")
    producto = load_csv("Data/Producto.csv")
    orden_etapa = load_csv("Data/Orden etapa.csv")  
    semana = load_csv("Data/Semana.csv")


    # Corrige columnas con BOM si existen
    rename_map = {
        "ï»¿NumeroOperacion": "NumeroOperacion",
        "ï»¿CodigoTipoContacto": "CodigoTipoContacto",
        "ï»¿Producto": "Producto",
        "ï»¿Etapa": "Etapa",
        "ï»¿DiaSemana": "DiaSemana"
    }

    df.rename(columns=rename_map, inplace=True)
    tipo_contacto.rename(columns=rename_map, inplace=True)
    producto.rename(columns=rename_map, inplace=True)
    orden_etapa.rename(columns=rename_map, inplace=True)
    semana.rename(columns=rename_map, inplace=True)

    # uniones
    df = df.merge(tipo_contacto, on="CodigoTipoContacto", how="left")

    df = df.merge(
        producto[["ProductoGestion", "Producto"]],
        on="ProductoGestion",
        how="left"
    )

    df = df.merge(orden_etapa, on="Etapa", how="left")

    semana.rename(columns={"fechaGestion": "FechaGestion"}, inplace=True)

    df = df.merge(semana, on="FechaGestion", how="left")


    # ========= CAMPOS CALCULADOS =========
    
    # EsContactoDirecto (como DAX)
    df["EsContactoDirecto"] = (df["CodigoTipoContacto"] == "TIPRESCDIRE").astype(int)
    
    # EsContacto (como DAX)
    df["EsContacto"] = (df["CodigoTipoContacto"] != "TIPRESNCON").astype(int)

    # Robot (como DAX)
    df["Robot"] = df["EsGestor"].apply(lambda x: "GESTOR" if x == 1 else "GESTOR_")

    
    # Métricas del panel
    df["Gestiones"] = 1
    df["CD"] = df["EsContactoDirecto"]
    df["Contacto"] = df["EsContacto"]
    df["ContactoDirecto"] = df["EsContactoDirecto"]
    df["Compromisos"] = df["EsCompromiso"]


    return df


df = load_all()

# =========================================================
# INTERFAZ PRINCIPAL
# =========================================================
tab1, tab2, tab3 = st.tabs([" Gestiones", " Detalle", " Comparativo"])


# =========================================================
# 1️⃣ — PESTAÑA GESTIONES (Ventana 1 Power BI)
# =========================================================
with tab1:

    st.title(" Panel de Gestiones — Productividad BS")

    # -------------------- FILTROS --------------------
    st.markdown("###  Filtros")

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)


    with c1:
        fecha_sel = st.selectbox("Fecha Gestión", ["Todas"] + sorted(df["FechaGestion"].dropna().unique()))

    with c2:
        supervisor_sel = st.selectbox("Supervisor", ["Todas"] + sorted(df["Supervisor"].dropna().unique()))

    with c3:
        gestor_sel = st.selectbox("Gestor", ["Todas"] + sorted(df["Gestor"].dropna().unique()))

    with c4:
        etapa_sel = st.selectbox("Etapa", ["Todas"] + sorted(df["Etapa"].dropna().unique()))

    with c5:
        estrategia_sel = st.selectbox("Estrategia", ["Todas"] + sorted(df["Estrategia"].dropna().unique()))

    with c6:
        producto_sel = st.selectbox("Producto", ["Todos"] + sorted(df["Producto"].dropna().unique()))
    with c7:
        tipo_sel = st.selectbox("Tipo", ["Todos"] + sorted(df["Robot"].unique()))


    # Aplicar filtros
    df_f = df.copy()

    if fecha_sel != "Todas":
        df_f = df_f[df_f["FechaGestion"] == fecha_sel]

    if supervisor_sel != "Todas":
        df_f = df_f[df_f["Supervisor"] == supervisor_sel]

    if gestor_sel != "Todas":
        df_f = df_f[df_f["Gestor"] == gestor_sel]

    if etapa_sel != "Todas":
        df_f = df_f[df_f["Etapa"] == etapa_sel]

    if estrategia_sel != "Todas":
        df_f = df_f[df_f["Estrategia"] == estrategia_sel]

    if producto_sel != "Todos":
        df_f = df_f[df_f["Producto"] == producto_sel]
        
    if tipo_sel != "Todos":
        df_f = df_f[df_f["Robot"] == tipo_sel]



    # -------------------- KPIs --------------------
    st.markdown("---")
    st.markdown("###  Métricas")

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric("Gestiones", df_f["Gestiones"].sum())
    k2.metric("Operaciones Únicas", df_f["NumeroOperacion"].nunique())
    k3.metric("Contacto Directo", df_f["Contacto"].sum())
    k4.metric("Directo", df_f["ContactoDirecto"].sum())
    k5.metric("Compromisos", df_f["Compromisos"].sum())


    # --------------------------------------------------------
    # LAYOUT PRINCIPAL
    # --------------------------------------------------------
    st.markdown("---")
    colA, colB, colC = st.columns([1.2, 1.3, 1])

    # ----------- 1) Tabla primera gestión -----------
    with colA:
        st.markdown("####  Hora de la primera gestión")

        df_hora = (
            df_f.groupby("Gestor")["HoraGestion"]
            .min()
            .reset_index()
            .sort_values("HoraGestion")
        )

        st.dataframe(df_hora, use_container_width=True, height=360)


    # ----------- 2) Slider + funnel -----------
    with colB:
        st.markdown("####  Rango de hora")

        h_min = int(df_f["Hora"].min())
        h_max = int(df_f["Hora"].max())

        desde = st.slider("Desde", h_min, h_max, h_min)
        hasta = st.slider("Hasta", h_min, h_max, h_max)

        df_rango = df_f[(df_f["Hora"] >= desde) & (df_f["Hora"] <= hasta)]

        st.markdown(f"**Gestiones en rango:** {df_rango['Gestiones'].sum():,.0f}")

        funnel = pd.DataFrame({
            "Etapa": ["Operaciones", "Contacto Directo", "Directo", "Compromisos"],
            "Valor": [
                df_rango["NumeroOperacion"].nunique(),
                df_rango["Contacto"].sum(),
                df_rango["ContactoDirecto"].sum(),
                df_rango["Compromisos"].sum(),
            ]
        })

        fig = px.bar(
            funnel,
            x="Valor",
            y="Etapa",
            orientation="h",
            text="Valor"
        )
        st.plotly_chart(fig, use_container_width=True, height=360)


    # ----------- 3) Donut Tipo Contacto -----------
    with colC:
        st.markdown("#### Tipo de contacto")

        tc = df_f["TipoContacto"].value_counts().reset_index()
        tc.columns = ["Tipo", "Cantidad"]

        fig_pie = px.pie(tc, values="Cantidad", names="Tipo", hole=0.55)
        st.plotly_chart(fig_pie, use_container_width=True, height=360)


    # -------------------- TABLAS INFERIORES --------------------
    st.markdown("---")
    b1, b2 = st.columns([1.2, 1.8])

    # ----------- Resumen por gestor -----------
    with b1:
        st.markdown("####  Resumen por Gestor")

        tabla = (
            df_f.groupby("Gestor")
            .agg({
                "Gestiones": "sum",
                "CD": "sum",
                "Compromisos": "sum",
                "ContactoDirecto": "sum",
            })
            .reset_index()
        )

        tabla["% Directo"] = (tabla["ContactoDirecto"] / tabla["Gestiones"] * 100).round(1)

        st.dataframe(tabla, use_container_width=True, height=320)


    # ----------- Tabla por hora -----------
    with b2:
        st.markdown("#### Gestiones por Hora")

        tabla_horas = pd.pivot_table(
            df_f,
            index="Gestor",
            columns="Hora",
            values="Gestiones",
            aggfunc="sum",
            fill_value=0
        )

        st.dataframe(tabla_horas, use_container_width=True, height=320)



# =========================================================
# 6. PESTAÑA — DETALLE
# =========================================================
with tab2:

    st.title(" Detalle de Gestiones")

    # -------------------- FILTROS --------------------
    st.markdown("###  Filtros")

    d1, d2, d3, d4, d5, d6, d7 = st.columns(7)

    with d1:
        fecha_d = st.selectbox("Fecha Gestión", ["Todas"] + sorted(df["FechaGestion"].dropna().unique()))

    with d2:
        supervisor_d = st.selectbox("Supervisor", ["Todas"] + sorted(df["Supervisor"].dropna().unique()))

    with d3:
        gestor_d = st.selectbox("Gestor", ["Todas"] + sorted(df["Gestor"].dropna().unique()))

    with d4:
        etapa_d = st.selectbox("Etapa", ["Todas"] + sorted(df["Etapa"].dropna().unique()))

    with d5:
        estrategia_d = st.selectbox("Estrategia", ["Todas"] + sorted(df["Estrategia"].dropna().unique()))

    with d6:
        producto_d = st.selectbox("Producto", ["Todos"] + sorted(df["Producto"].dropna().unique()))

    with d7:
        tipo_d = st.selectbox("Tipo", ["Todos"] + sorted(df["Robot"].dropna().unique()))

    # Aplicar filtros
    df_det = df.copy()

    if fecha_d != "Todas":
        df_det = df_det[df_det["FechaGestion"] == fecha_d]

    if supervisor_d != "Todas":
        df_det = df_det[df_det["Supervisor"] == supervisor_d]

    if gestor_d != "Todas":
        df_det = df_det[df_det["Gestor"] == gestor_d]

    if etapa_d != "Todas":
        df_det = df_det[df_det["Etapa"] == etapa_d]

    if estrategia_d != "Todas":
        df_det = df_det[df_det["Estrategia"] == estrategia_d]

    if producto_d != "Todos":
        df_det = df_det[df_det["Producto"] == producto_d]

    if tipo_d != "Todos":
        df_det = df_det[df_det["Robot"] == tipo_d]

    # -------------------- GRAFICOS --------------------
    st.markdown("---")
    g1, g2 = st.columns(2)

    # ----------- Gráfico 1: Respuestas ----------- 
    with g1:
        st.markdown("#### Respuestas más frecuentes")

        if "Respuesta" in df_det.columns:
            resp = df_det["Respuesta"].value_counts().reset_index()
            resp.columns = ["Respuesta", "Cantidad"]

            fig_resp = px.bar(
                resp,
                y="Respuesta",
                x="Cantidad",
                orientation="h",
                text="Cantidad"
            )
            st.plotly_chart(fig_resp, use_container_width=True, height=400)
        else:
            st.info("No existe la columna 'Respuesta' en los datos.")

    # ----------- Gráfico 2: Tipo de Contacto ----------- 
    with g2:
        st.markdown("#### Tipo de Contacto")

        tc = df_det["TipoContacto"].value_counts().reset_index()
        tc.columns = ["TipoContacto", "Cantidad"]

        fig_tc = px.bar(
            tc,
            y="TipoContacto",
            x="Cantidad",
            orientation="h",
            text="Cantidad"
        )
        st.plotly_chart(fig_tc, use_container_width=True, height=400)

    # -------------------- TABLA DETALLE --------------------
    st.markdown("---")
    st.markdown("###  Registros detallados")

    columnas_detalle = [
        "Gestor",
        "Identificacion",
        "Telefono",
        "HoraGestion",
        "Respuesta",
        "TipoContacto",
        "CodigoTipoContacto",
        "Robot"
    ]

    # Filtrar columnas existentes
    columnas_presentes = [c for c in columnas_detalle if c in df_det.columns]

    df_final = df_det[columnas_presentes].sort_values("HoraGestion")

    st.dataframe(df_final, use_container_width=True, height=650)

