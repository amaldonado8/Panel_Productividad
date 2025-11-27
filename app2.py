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

    # limpiar BOM, espacios, caracteres invisibles
    df.columns = (
        df.columns
        .str.replace("ï»¿", "", regex=False)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    return df


# =========================================================
# 1. Cargar archivos
# =========================================================
@st.cache_data
def load_all():

    # CARGAR LOS 5 ARCHIVOS DE GESTIONES
    gestion_files = [
        "Data/Gestion_part1.csv",
        "Data/Gestion_part2.csv",
        "Data/Gestion_part3.csv",
        "Data/Gestion_part4.csv",
        "Data/Gestion_part5.csv"
    ]

    df_list = [load_csv(f) for f in gestion_files]

    # UNIR TODO EN UN SOLO DATAFRAME
    df = pd.concat(df_list, ignore_index=True)

    # Cargar otras tablas
    tipo_contacto = load_csv("Data/TipoContacto.csv")
    producto = load_csv("Data/Producto.csv")
    orden_etapa = load_csv("Data/Orden etapa.csv")
    semana = load_csv("Data/Semana.csv")

    # ------------------------------
    # Renombrar columnas con BOM
    # ------------------------------
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

    # =====================================================
    # 2. Uniones como en Power BI
    # =====================================================

    # Tipo de Contacto
    df = df.merge(
        tipo_contacto,
        on="CodigoTipoContacto",
        how="left"
    )

    # Producto
    df = df.merge(
        producto[["ProductoGestion", "Producto"]],
        on="ProductoGestion",
        how="left"
    )

    # Orden Etapa
    df = df.merge(
        orden_etapa,
        on="Etapa",
        how="left"
    )

    # Semana: renombrar para hacer merge
    semana.rename(columns={"fechaGestion": "FechaGestion"}, inplace=True)

    df = df.merge(
        semana,
        on="FechaGestion",
        how="left"
    )

    # =====================================================
    # 3. Crear métricas del panel
    # =====================================================
    df["Gestiones"] = 1
    df["CD"] = df["EsContactoDirecto"]
    df["Contacto"] = df["EsContacto"]
    df["ContactoDirecto"] = df["EsContactoDirecto"]
    df["Compromisos"] = df["EsCompromiso"]

    return df


df = load_all()


# =========================================================
# 4. INTERFAZ PRINCIPAL
# =========================================================
tab1, tab2, tab3 = st.tabs([" Gestiones", " Detalle", " Comparativo"])


# =========================================================
# 5. PESTAÑA — GESTIONES
# =========================================================
with tab1:

    st.title(" Panel de Gestiones — Productividad BS")

    # -------------------- FILTROS --------------------
    st.markdown("###  Filtros")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

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


    # -------------------- KPIs --------------------
    st.markdown("---")
    st.markdown("###  Métricas")

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.metric("Gestiones", df_f["Gestiones"].sum())

    with k2:
        st.metric("Operaciones Únicas", df_f["NumeroOperacion"].nunique())

    with k3:
        st.metric("Contacto", df_f["Contacto"].sum())

    with k4:
        st.metric("Directo", df_f["ContactoDirecto"].sum())

    with k5:
        st.metric("Compromisos", df_f["Compromisos"].sum())


    # -------------------- LAYOUT PRINCIPAL --------------------
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

        h1, h2 = st.columns(2)

        with h1:
            desde = st.slider("Desde", h_min, h_max, h_min)

        with h2:
            hasta = st.slider("Hasta", h_min, h_max, h_max)

        df_rango = df_f[(df_f["Hora"] >= desde) & (df_f["Hora"] <= hasta)]

        st.markdown(f"**Gestiones en rango:** {df_rango['Gestiones'].sum():,.0f}")

        funnel = pd.DataFrame({
            "Etapa": ["Operaciones", "Contacto", "Directo", "Compromisos"],
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

    # ----------- Tabla resumen gestor -----------
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
# Placeholders de las otras pestañas
# =========================================================
# =========================================================
# 6. PESTAÑA — DETALLE
# =========================================================
with tab2:

    st.title(" Detalle de Gestiones")

    # -------------------- FILTROS --------------------
    st.markdown("###  Filtros")

    d1, d2, d3, d4, d5, d6 = st.columns(6)

    with d1:
        fecha_d = st.selectbox("Fecha Gestión — Detalle", ["Todas"] + sorted(df["FechaGestion"].dropna().unique()))

    with d2:
        supervisor_d = st.selectbox("Supervisor — Detalle", ["Todas"] + sorted(df["Supervisor"].dropna().unique()))

    with d3:
        gestor_d = st.selectbox("Gestor — Detalle", ["Todas"] + sorted(df["Gestor"].dropna().unique()))

    with d4:
        etapa_d = st.selectbox("Etapa — Detalle", ["Todas"] + sorted(df["Etapa"].dropna().unique()))

    with d5:
        estrategia_d = st.selectbox("Estrategia — Detalle", ["Todas"] + sorted(df["Estrategia"].dropna().unique()))

    with d6:
        producto_d = st.selectbox("Producto — Detalle", ["Todos"] + sorted(df["Producto"].dropna().unique()))

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

    # -------------------- GRAFICOS --------------------
    st.markdown("---")
    g1, g2 = st.columns(2)

    # ----------- Gráfico 1: Respuestas -----------
    with g1:
        st.markdown("#### Respuestas más frecuentes")
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
    st.markdown("### 📋 Registros detallados")

    columnas_detalle = [
        "Gestor",
        "Identificacion",
        "Telefono",
        "HoraGestion",
        "Respuesta",
        "TipoContacto",
        "Observacion"
    ]

    columnas_presentes = [c for c in columnas_detalle if c in df_det.columns]

    df_final = df_det[columnas_presentes].sort_values("HoraGestion")

    st.dataframe(df_final, use_container_width=True, height=650)


# =========================================================
# 7. PESTAÑA — COMPARATIVO (CORREGIDO)
# =========================================================

with tab3:

    st.title(" Comparativo de Productividad")

    # -------------------- FILTROS --------------------
    st.markdown("### Filtros")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        fecha_c = st.selectbox(
            "Fecha Gestión — Comp.",
            ["Todas"] + sorted(df["Fecha"].dropna().unique()),
            key="fc3"
        )

    with c2:
        supervisor_c = st.selectbox(
            "Supervisor — Comp.",
            ["Todas"] + sorted(df["Supervisor"].dropna().unique()),
            key="sc3"
        )

    with c3:
        gestor_c = st.selectbox(
            "Gestor — Comp.",
            ["Todas"] + sorted(df["Gestor"].dropna().unique()),
            key="gc3"
        )

    with c4:
        etapa_c = st.selectbox(
            "Etapa — Comp.",
            ["Todas"] + sorted(df["Etapa"].dropna().unique()),
            key="ec3"
        )

    with c5:
        estrategia_c = st.selectbox(
            "Estrategia — Comp.",
            ["Todas"] + sorted(df["Estrategia"].dropna().unique()),
            key="es3"
        )

    with c6:
        producto_c = st.selectbox(
            "Producto — Comp.",
            ["Todos"] + sorted(df["Producto"].dropna().unique()),
            key="pc3"
        )


    # -------------------- APLICAR FILTROS --------------------
    df_c = df.copy()

    if fecha_c != "Todas":
        df_c = df_c[df_c["Fecha"] == fecha_c]

    if supervisor_c != "Todas":
        df_c = df_c[df_c["Supervisor"] == supervisor_c]

    if gestor_c != "Todas":
        df_c = df_c[df_c["Gestor"] == gestor_c]

    if etapa_c != "Todas":
        df_c = df_c[df_c["Etapa"] == etapa_c]

    if estrategia_c != "Todas":
        df_c = df_c[df_c["Estrategia"] == estrategia_c]

    if producto_c != "Todos":
        df_c = df_c[df_c["Producto"] == producto_c]


    # -------------------- SLIDER HORA --------------------
    st.markdown("---")
    st.subheader("Rango de Hora")

    h_min_c = int(df_c["Hora"].min())
    h_max_c = int(df_c["Hora"].max())

    col_h1, col_h2 = st.columns(2)

    with col_h1:
        desde_c = st.slider("Desde", h_min_c, h_max_c, h_min_c, key="hmin_c3")

    with col_h2:
        hasta_c = st.slider("Hasta", h_min_c, h_max_c, h_max_c, key="hmax_c3")

    df_c_rango = df_c[(df_c["Hora"] >= desde_c) & (df_c["Hora"] <= hasta_c)]


    # -------------------- GRÁFICO COMPARATIVO --------------------
    st.markdown("---")
    st.subheader("Comparativo por Tipo de Contacto y Día")

    # Verificar columnas de Semana.csv
    if "MesDia" not in df_c_rango.columns:
        st.error("❌ La columna 'MesDia' no existe. Revisa Semana.csv")
    else:
        comp = (
            df_c_rango.groupby(["TipoContacto", "MesDia"])
            .agg({"Gestiones": "sum"})
            .reset_index()
        )

        if comp.empty:
            st.warning("⚠️ No hay datos para mostrar con los filtros seleccionados.")
        else:
            fig_comp = px.bar(
                comp,
                x="TipoContacto",
                y="Gestiones",
                color="MesDia",
                barmode="group",
                text="Gestiones"
            )

            st.plotly_chart(fig_comp, use_container_width=True, height=420)


    # -------------------- TABLA COMPARATIVA --------------------
    st.markdown("---")
    st.subheader("Tabla Comparativa por Gestor y Día")

    tabla = (
        df_c_rango.groupby(["Gestor", "MesDia"])
        .agg({
            "Gestiones": "sum",
            "ContactoDirecto": "sum",
            "Compromisos": "sum",
            "HoraGestion": "min"
        })
        .reset_index()
    )

    if not tabla.empty:

        tabla_pivot = tabla.pivot_table(
            index="Gestor",
            columns="MesDia",
            values=["Gestiones", "ContactoDirecto", "Compromisos", "HoraGestion"],
            aggfunc="first"
        )

        tabla_pivot.columns = [f"{col2} {col1}" for col1, col2 in tabla_pivot.columns]

        tabla_pivot = tabla_pivot.reset_index()

        st.dataframe(tabla_pivot, use_container_width=True, height=650)
    else:
        st.warning("⚠️ No hay registros para la tabla comparativa con los filtros actuales.")



