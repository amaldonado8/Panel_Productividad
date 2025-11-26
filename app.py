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

