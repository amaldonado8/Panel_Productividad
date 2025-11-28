import pyodbc
import pandas as pd
import datetime
import traceback

SERVER = r"SICCUBOCL\\INSTBDD01"
DATABASE = "Reportes"

OUTPUT_PATH = r"C:\Users\amaldonado\OneDrive - Sicontac Center S.A\Documentos\Documentos Analytics\Paneles\Aplicacion_Panel\Data\gestiones_actualizado.csv"

QUERY = """
select skfecha,
       DATEPART(hour, horagestion) as Hora,
       cast(CONVERT(varchar(10), FechaGestion) +' '+ CONVERT(varchar(11), HoraGestion) as datetime) AS Fecha,
       FechaGestion,
       CONVERT(varchar, HoraGestion, 8) HoraGestion,
       NumeroOperacion,
       tipocontacto as CodigoTipoContacto,
       NombreRespuesta as Respuesta,
       Identificacion,
       Telefono,
       Etapa,
       codigoCedente as Cedente,
       EsCompromiso,
       TiempoGestion,
       ProductoGestion,
       EsGestor,
       esEfectivo,
    
       Estrategia,
       Gestor,
       Supervisor,
       codigocanal,
       EstadoCompromiso
from RepGestionesSemanalPorHora
where CodigoCedente = 'SOLIDARIO'
  and codigocanal in ('CALLCENTER','TELECONTACT')
  and CAST(FechaGestion AS DATE) = '2025-11-21'

"""

def run_query():
    try:
        print("Conectando al servidor SQL...")

        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "Server=SICCUBOCL\\INSTBDD01;"
            "Database=Reportes;"
            "Trusted_Connection=yes;"
        )

        conn = pyodbc.connect(conn_str)
        print("Conexión exitosa.")

        df = pd.read_sql_query(QUERY, conn)

        print(f"Filas obtenidas: {len(df)}")

        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"Archivo actualizado: {OUTPUT_PATH}")

        conn.close()

    except Exception:
        print("Error ejecutando el proceso:")
        print(traceback.format_exc())


if __name__ == "__main__":
    print("---- EJECUCIÓN INICIADA ----", datetime.datetime.now())
    run_query()
    print("---- EJECUCIÓN TERMINADA ----", datetime.datetime.now())