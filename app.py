@st.cache_data
def load_all():

    # =====================================================
    # 1. Cargar TODOS los archivos de gestiones
    # =====================================================
    gestion_files = [
        "Data/Gestion_part1.csv",
        "Data/Gestion_part2.csv",
        "Data/Gestion_part3.csv",
        "Data/Gestion_part4.csv",
        "Data/Gestion_part5.csv"
    ]

    df_list = []

    for f in gestion_files:
        tmp = load_csv(f)
        df_list.append(tmp)

    df = pd.concat(df_list, ignore_index=True)

    # =====================================================
    # 2. Cargar tablas complementarias
    # =====================================================
    tipo_contacto = load_csv("Data/TipoContacto.csv")
    producto = load_csv("Data/Producto.csv")
    orden_etapa = load_csv("Data/Orden etapa.csv")
    semana = load_csv("Data/Semana.csv")

    # =====================================================
    # 3. LIMPIEZA PROFUNDA DE COLUMNAS (BOM, espacios)
    # =====================================================
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

    # LIMPIAR TODAS LAS COLUMNAS DEL ARCHIVO PRODUCTO
    producto.columns = (
        producto.columns
        .str.replace("ï»¿", "", regex=False)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    # LIMPIAR VALORES DE PRODUCTO EN AMBOS DATASETS
    producto["ProductoGestion"] = producto["ProductoGestion"].str.strip()
    df["ProductoGestion"] = df["ProductoGestion"].str.strip()

    # LIMPIAR "Etapa" Y "CodigoTipoContacto" TAMBIÉN
    df["Etapa"] = df["Etapa"].str.strip()
    df["CodigoTipoContacto"] = df["CodigoTipoContacto"].str.strip()

    tipo_contacto["CodigoTipoContacto"] = tipo_contacto["CodigoTipoContacto"].str.strip()
    orden_etapa["Etapa"] = orden_etapa["Etapa"].str.strip()

    # =====================================================
    # 4. Uniones (exactamente como en Power BI)
    # =====================================================

    # Tipo de Contacto
    df = df.merge(
        tipo_contacto,
        on="CodigoTipoContacto",
        how="left"
    )

    # Producto Categoria Final (ALIA, CCO, MICROCREDITO, ETC)
    df = df.merge(
        producto[["ProductoGestion", "Producto"]],
        on="ProductoGestion",
        how="left"
    )

    # Orden de Etapa
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
    # 5. Crear columnas métricas del panel
    # =====================================================
    df["Gestiones"] = 1
    df["Contacto"] = df["EsContacto"]
    df["ContactoDirecto"] = df["EsContactoDirecto"]
    df["Compromisos"] = df["EsCompromiso"]
    df["CD"] = df["EsContactoDirecto"]

    return df

