import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Panel Productividad BS", layout="wide")

# =========================================================
# 1. Cargar los CSVs
# =========================================================
@st.cache_data
def load_all():
    df = pd.read_csv("Data/Gestion_part1.csv", sep=";", encoding="latin-1")
    tipo_contacto = pd.read_csv("Data/TipoContacto.csv", sep=";", encoding="latin-1")
    producto = pd.read_csv("Data/Producto.csv", sep=";", encoding="latin-1")
    orden_etapa = pd.read_csv("Data/Orden etapa.csv", sep=";", encoding="latin-1")
    semana = pd.read_csv("Data/Semana.csv", sep=";", encoding="latin-1")

    # -----------------------------------------
    # 2. Uniones como en Power BI
    # -----------------------------------------

    # Tipo Contacto
    df = df.merge(
        tipo_contacto,
        left_on="CodigoTipoContacto",
        right_on="CodigoTipoContacto",
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

    # Semana / Fecha
    df = df.merge(
        semana[["fechaGestion", "DiaSemana", "MesDia"]],
        left_on="FechaGestion",
        right_on="fechaGestion",
        how="left"
    )

    # -----------------------------------------
    # 3. Crear métricas como en Power BI
    # -----------------------------------------
    df["Gestiones"] = 1
    df["Contacto"] = df["EsContacto"]
    df["ContactoDirecto"] = df["EsContactoDirecto"]
    df["Compromisos"] = df["EsCompromiso"]
    df["CD"] = df["EsContactoDirecto"]

    return df


df = load_all()

# =========================================================
# 4. Estructura con pestañas
# =========================================================
tab1, tab2, tab3 = st.tabs(["📊 Gestiones", "📄 Detalle", "📈 Comparativo"])



# =========================================================
# 5. PRIMERA VENTANA
# =========================================================
with tab1:

    st.title("📊 Panel de Gestiones – Productividad BS")

    # ---------------------------
    #    FILTROS SUPERIORES
    # ---------------------------
    st.markdown("### 🔎 Filtros")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        fecha_sel = st.selectbox(
            "Fecha Gestión",
            ["Todas"] + sorted(df["FechaGestion"].dropna().unique())
        )

    with c2:
        supervisor_sel = st.selectbox(
            "Supervisor",
            ["Todas"] + sorted(df["Supervisor"].dropna().unique())
        )

    with c3:
        gestor_sel = st.selectbox(
            "Gestor",
            ["Todas"] + sorted(df["Gestor"].dropna().unique())
        )

    with c4:
        etapa_sel = st.selectbox(
            "Etapa",
            ["Todas"] + sorted(df["Etapa"].dropna().unique())
        )

    with c5:
        estrategia_sel = st.selectbox(
            "Estrategia",
            ["Todas"] + sorted(df["Estrategia"].dropna().unique())
        )

    with c6:
        producto_sel = st.selectbox(
            "Producto",
            ["Todos"] + sorted(df["Producto"].dropna().unique())
        )

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


    # ---------------------------
    #          KPIs
    # ---------------------------
    st.markdown("---")
    st.markdown("### 📌 Indicadores Principales")

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        st.metric("Gestiones", f"{df_f['Gestiones'].sum():,.0f}")

    with k2:
        st.metric("N° Operaciones", f"{df_f['NumeroOperacion'].nunique():,.0f}")

    with k3:
        st.metric("Contacto", f"{df_f['Contacto'].sum():,.0f}")

    with k4:
        st.metric("Directo", f"{df_f['ContactoDirecto'].sum():,.0f}")

    with k5:
        st.metric("Compromisos", f"{df_f['Compromisos'].sum():,.0f}")


    # ---------------------------
    #  3 COLUMNAS PRINCIPALES
    # ---------------------------
    st.markdown("---")
    colA, colB, colC = st.columns([1.2, 1.2, 1])



    # ----------- TABLA HORA PRIMERA GESTIÓN -----------
    with colA:
        st.markdown("#### 🕒 Hora de la primera gestión")

        df_hora = (
            df_f.groupby("Gestor")["HoraGestion"]
            .min()
            .reset_index()
            .sort_values("HoraGestion")
        )

        st.dataframe(df_hora, use_container_width=True)


    # ----------- SLIDER + FUNNEL -----------
    with colB:
        st.markdown("#### ⏳ Rango de Hora")

        hora_min = int(df_f["Hora"].min())
        hora_max = int(df_f["Hora"].max())

        h1, h2 = st.columns(2)

        with h1:
            desde = st.slider("Desde", hora_min, hora_max, hora_min)

        with h2:
            hasta = st.slider("Hasta", hora_min, hora_max, hora_max)

        df_hor = df_f[(df_f["Hora"] >= desde) & (df_f["Hora"] <= hasta)]

        st.markdown(f"**Total gestiones:** {df_hor['Gestiones'].sum():,.0f}")

        funnel = pd.DataFrame({
            "Etapa": ["Operaciones", "Contacto", "Directo", "Compromisos"],
            "Valor": [
                df_hor["NumeroOperacion"].nunique(),
                df_hor["Contacto"].sum(),
                df_hor["ContactoDirecto"].sum(),
                df_hor["Compromisos"].sum(),
            ]
        })

        fig_fun = px.bar(
            funnel,
            x="Valor",
            y="Etapa",
            orientation="h",
            text="Valor"
        )
        st.plotly_chart(fig_fun, use_container_width=True)



    # ----------- PIE TIPO CONTACTO -----------
    with colC:
        st.markdown("#### 📞 Tipo de Contacto")

        tc = df_f["TipoContacto"].value_counts().reset_index()
        tc.columns = ["Tipo", "Cantidad"]

        fig_pie = px.pie(tc, values="Cantidad", names="Tipo", hole=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)



    # ---------------------------
    # TABLAS INFERIORES
    # ---------------------------
    st.markdown("---")
    b1, b2 = st.columns([1.2, 1.8])

    # ----------- TABLA RESUMEN GESTOR -----------
    with b1:
        st.markdown("#### 📋 Resumen por Gestor")

        resumen = (
            df_f.groupby("Gestor")
            .agg({
                "Gestiones": "sum",
                "CD": "sum",
                "Compromisos": "sum",
                "ContactoDirecto": "sum",
            })
            .reset_index()
        )

        resumen["% Directo"] = (resumen["ContactoDirecto"] / resumen["Gestiones"] * 100).round(1)

        st.dataframe(resumen, use_container_width=True)


    # ----------- TABLA GESTIONES POR HORA -----------
    with b2:
        st.markdown("#### 📊 Gestiones por Hora")

        tabla_horas = pd.pivot_table(
            df_f,
            index="Gestor",
            columns="Hora",
            values="Gestiones",
            aggfunc="sum",
            fill_value=0
        )

        st.dataframe(tabla_horas, use_container_width=True)



# =========================================================
# PLACEHOLDER PESTAÑAS 2 Y 3
# =========================================================
with tab2:
    st.info("Próximamente: pestaña Detalle.")

with tab3:
    st.info("Próximamente: pestaña Comparativo.")


