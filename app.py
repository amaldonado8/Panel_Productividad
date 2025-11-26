import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Panel Productividad BS", layout="wide")

# =========================================================
# 1. CARGA DE DATOS
# =========================================================
@st.cache_data
def load_data():
    """
    Carga el archivo principal de gestiones.
    Asegúrate de que el archivo exista en: Data/Gestion_part1.csv
    """
    path = "Data/Gestion_part1.csv"
    try:
        df = pd.read_csv(path, encoding="latin-1")
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo {path}. Verifica el nombre y la ruta.")
        st.stop()
    return df


df_raw = load_data()

# =========================================================
# 2. VALIDAR COLUMNAS NECESARIAS
#    (ajusta aquí si tus nombres son diferentes)
# =========================================================
required_cols = [
    "FechaGestion",      # fecha de gestión
    "Supervisor",
    "Gestor",
    "Etapa",
    "Estrategia",
    "Tipo",              # tipo de cartera / gestión
    "Producto",          # ALIA, ALIA MI SOCIA, etc.
    "Hora",              # hora (entera 0-23)
    "HoraGestion",       # hora de la primera gestión
    "Gestiones",
    "NumeroOperaciones",
    "Contacto",
    "ContactoDirecto",
    "Compromisos",
    "CD",
    "TipoContacto"
]

missing = [c for c in required_cols if c not in df_raw.columns]

if missing:
    st.error(
        "❌ Faltan columnas en tu archivo CSV para reproducir la primera ventana.\n\n"
        "Columnas faltantes:\n"
        + "\n".join(f"- {c}" for c in missing)
        + "\n\nRevisa los nombres en Gestion_part1.csv o ajústalos en el código."
    )
    st.stop()

df = df_raw.copy()

# =========================================================
# 3. ESTRUCTURA DE LA APP CON PESTAÑAS
# =========================================================
tab1, tab2, tab3 = st.tabs(["📊 Gestiones", "📄 Detalle", "📈 Comparativo"])

# =========================================================
# 4. PESTAÑA 1: GESTIONES
# =========================================================
with tab1:
    st.title("Panel Productividad BS – Gestiones")

    # ------------------ 4.1 Filtros superiores ------------------
    st.markdown("### 🔎 Filtros")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        fecha_sel = st.selectbox(
            "Fecha Gestión",
            ["Todas"] + sorted(df["FechaGestion"].dropna().unique().tolist())
        )

    with c2:
        supervisor_sel = st.selectbox(
            "Supervisor",
            ["Todas"] + sorted(df["Supervisor"].dropna().unique().tolist())
        )

    with c3:
        gestor_sel = st.selectbox(
            "Gestor",
            ["Todas"] + sorted(df["Gestor"].dropna().unique().tolist())
        )

    with c4:
        etapa_sel = st.selectbox(
            "Etapa",
            ["Todas"] + sorted(df["Etapa"].dropna().unique().tolist())
        )

    with c5:
        estrategia_sel = st.selectbox(
            "Estrategia",
            ["Todas"] + sorted(df["Estrategia"].dropna().unique().tolist())
        )

    with c6:
        tipo_sel = st.selectbox(
            "Tipo",
            ["Todas"] + sorted(df["Tipo"].dropna().unique().tolist())
        )

    # “Botones” de producto (ALIA, ALIA MI SOCIA, etc.)
    st.markdown("### 🎯 Producto / Campaña")
    productos_unicos = ["Todos"] + sorted(df["Producto"].dropna().unique().tolist())
    producto_sel = st.segmented_control("Producto", productos_unicos, key="producto_seg")

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

    if tipo_sel != "Todas":
        df_f = df_f[df_f["Tipo"] == tipo_sel]

    if producto_sel != "Todos":
        df_f = df_f[df_f["Producto"] == producto_sel]

    if df_f.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        st.stop()

    # ------------------ 4.2 Métricas principales ------------------
    st.markdown("---")
    st.markdown("### 📌 Indicadores generales")

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric("Gestiones", f"{df_f['Gestiones'].sum():,.0f}")

    with m2:
        st.metric("Número de Operaciones", f"{df_f['NumeroOperaciones'].sum():,.0f}")

    with m3:
        st.metric("Contacto", f"{df_f['Contacto'].sum():,.0f}")

    with m4:
        st.metric("Contacto Directo", f"{df_f['ContactoDirecto'].sum():,.0f}")

    with m5:
        st.metric("Compromisos", f"{df_f['Compromisos'].sum():,.0f}")

    # ------------------ 4.3 Layout principal ------------------
    st.markdown("---")
    top_left, top_mid, top_right = st.columns([1.2, 1.2, 1])

    # ---- 4.3.1 Tabla: Hora de la primera gestión ----
    with top_left:
        st.markdown("#### 🕒 Hora de la primera gestión")

        df_hora = (
            df_f.groupby("Gestor")["HoraGestion"]
            .min()
            .reset_index()
            .sort_values("HoraGestion")
        )

        st.dataframe(df_hora, use_container_width=True, height=360)

    # ---- 4.3.2 Slider de hora + barras de embudo ----
    with top_mid:
        st.markdown("#### ⏳ Rango de hora")

        hora_min = int(df_f["Hora"].min())
        hora_max = int(df_f["Hora"].max())

        h1, h2 = st.columns(2)
        with h1:
            hora_desde = st.slider(
                "Desde",
                min_value=hora_min,
                max_value=hora_max,
                value=hora_min,
                key="hora_desde",
            )
        with h2:
            hora_hasta = st.slider(
                "Hasta",
                min_value=hora_min,
                max_value=hora_max,
                value=hora_max,
                key="hora_hasta",
            )

        df_rango = df_f[(df_f["Hora"] >= hora_desde) & (df_f["Hora"] <= hora_hasta)]

        st.markdown("#### Gestiones en rango seleccionado")
        st.markdown(
            f"**Total gestiones:** {df_rango['Gestiones'].sum():,.0f}",
        )

        # Gráfico tipo “embudo” horizontal (Operaciones → Contacto → Directo → Compromisos)
        funnel_data = pd.DataFrame(
            {
                "Etapa": [
                    "Número Operaciones",
                    "Contacto",
                    "Contacto Directo",
                    "Compromisos",
                ],
                "Valor": [
                    df_rango["NumeroOperaciones"].sum(),
                    df_rango["Contacto"].sum(),
                    df_rango["ContactoDirecto"].sum(),
                    df_rango["Compromisos"].sum(),
                ],
            }
        )

        fig_funnel = px.bar(
            funnel_data,
            x="Valor",
            y="Etapa",
            orientation="h",
            text="Valor",
        )
        fig_funnel.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_funnel.update_layout(
            yaxis_title="",
            xaxis_title="",
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
        )

        st.plotly_chart(fig_funnel, use_container_width=True)

    # ---- 4.3.3 Donut Tipo de Contacto ----
    with top_right:
        st.markdown("#### 📞 Tipo de contacto")

        contacto_counts = (
            df_f["TipoContacto"].value_counts().reset_index()
        )
        contacto_counts.columns = ["TipoContacto", "Cantidad"]

        if not contacto_counts.empty:
            fig_pie = px.pie(
                contacto_counts,
                values="Cantidad",
                names="TipoContacto",
                hole=0.6,
            )
            fig_pie.update_layout(
                legend_title_text="Tipo",
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay datos para TipoContacto con los filtros actuales.")

    # ------------------ 4.4 Parte inferior ------------------
    st.markdown("---")
    bottom_left, bottom_right = st.columns([1.2, 1.8])

    # ---- 4.4.1 Tabla resumen por gestor ----
    with bottom_left:
        st.markdown("#### 📋 Resumen por gestor")

        tabla_gen = (
            df_f.groupby("Gestor")
            .agg(
                Gestiones=("Gestiones", "sum"),
                CD=("CD", "sum"),
                Compromisos=("Compromisos", "sum"),
                ContactoDirecto=("ContactoDirecto", "sum"),
            )
            .reset_index()
        )

        tabla_gen["% Contacto Directo"] = (
            tabla_gen["ContactoDirecto"] / tabla_gen["Gestiones"] * 100
        )

        # Formatear porcentaje a 1 decimal
        tabla_gen["% Contacto Directo"] = tabla_gen["% Contacto Directo"].round(1)

        st.dataframe(tabla_gen, use_container_width=True, height=320)

    # ---- 4.4.2 Tabla dinámica: gestiones por hora ----
    with bottom_right:
        st.markdown("#### 📊 Gestiones por hora")

        tabla_horas = pd.pivot_table(
            df_f,
            index="Gestor",
            columns="Hora",
            values="Gestiones",
            aggfunc="sum",
            fill_value=0,
        )

        # ordenar columnas por hora
        tabla_horas = tabla_horas.reindex(sorted(tabla_horas.columns), axis=1)

        st.dataframe(tabla_horas, use_container_width=True, height=320)

# =========================================================
# 5. PESTAÑAS 2 Y 3 (PLACEHOLDER)
# =========================================================
with tab2:
    st.title("Detalle")
    st.info("Aquí construiremos la pestaña Detalle más adelante.")

with tab3:
    st.title("Comparativo")
    st.info("Aquí construiremos la pestaña Comparativo más adelante.")

