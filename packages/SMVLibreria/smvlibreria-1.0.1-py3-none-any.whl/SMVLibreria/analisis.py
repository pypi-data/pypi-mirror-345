# analisis.py

import pandas as pd
from carga_datos import cargar_csv_desde_url, guardar_csv_local


def contar_por_anio_trimestre_o_mes(df, periodo="trimestre"):
    
    # Cuenta las filas agrupadas por año, o por año y trimestre, o por año y mes, según la opción seleccionada.

    # Parámetros:
    #     df (pd.DataFrame): El DataFrame que contiene las columnas 'anio', 'trimestre' y 'mes'.
    #     periodo (str): Puede ser 'anio', 'trimestre' o 'mes'. Define cómo se agrupará el conteo.

    # Retorna:
    #     pd.DataFrame: DataFrame con el conteo por 'anio', 'anio y trimestre' o 'anio y mes'.
    
    # Verificar si las columnas necesarias están en el DataFrame
    if 'anio' not in df.columns or ('trimestre' not in df.columns and 'mes' not in df.columns):
        raise ValueError("El DataFrame debe contener las columnas 'anio', 'trimestre' y/o 'mes'")
    # Agrupar por 'anio', 'anio y trimestre' o 'anio y mes'
    if periodo == "anio":
        conteo = df.groupby(['anio']).size().reset_index(name="conteo")
    elif periodo == "trimestre":
        conteo = df.groupby(['anio', 'trimestre']).size().reset_index(name="conteo")
    elif periodo == "mes":
        conteo = df.groupby(['anio', 'mes']).size().reset_index(name="conteo")
    else:
        raise ValueError("El parámetro 'periodo' debe ser 'anio', 'trimestre' o 'mes'")

    return conteo


def tasa_crecimiento(df, periodo="anio", desde=None, hasta=None):
    
    # Calcula la tasa de crecimiento entre dos periodos específicos.

    # Parámetros:
    #     df (pd.DataFrame): DataFrame con columnas 'anio', 'trimestre' y/o 'mes'.
    #     periodo (str): Uno de 'anio', 'trimestre' o 'mes'.
    #     desde (tuple): Periodo inicial. Ej: (2019,), (2019, 1), o (2019, 1) dependiendo del tipo.
    #     hasta (tuple): Periodo final. Igual formato que 'desde'.

    # Retorna:
    #     float: Tasa de crecimiento (%)
    
     # Validación de entrada
    if periodo not in ["anio", "trimestre", "mes"]:
        raise ValueError("El parámetro 'periodo' debe ser 'anio', 'trimestre' o 'mes'")
    if desde is None or hasta is None:
        raise ValueError("Debes especificar los parámetros 'desde' y 'hasta'")

     # Agrupación según el periodo
    if periodo == "anio":
        grupo = df.groupby("anio").size()
        valor_desde = grupo.get(desde[0], 0)
        valor_hasta = grupo.get(hasta[0], 0)

    elif periodo == "trimestre":
        grupo = df.groupby(["anio", "trimestre"]).size()
        valor_desde = grupo.get((desde[0], desde[1]), 0)
        valor_hasta = grupo.get((hasta[0], hasta[1]), 0)

    elif periodo == "mes":
        grupo = df.groupby(["anio", "mes"]).size()
        valor_desde = grupo.get((desde[0], desde[1]), 0)
        valor_hasta = grupo.get((hasta[0], hasta[1]), 0)
    # Calcular tasa de crecimiento:
    if valor_desde == 0:
        raise ZeroDivisionError(f"No hay datos en el periodo desde {desde} (división por cero)")

    tasa = ((valor_hasta - valor_desde) / valor_desde) * 100
    return tasa


def main():
    url = "https://seguridadvial.semovi.cdmx.gob.mx/wp-content/themes/semovi-seguridad-vial/data/dataset.csv"
    df = cargar_csv_desde_url(url)
  
    if df is not None:
        print("Primeras filas del dataset:")
        print(df.head())

        # Guardarlo dataset localmente
        guardar_csv_local(df, "mi_dataset.csv")

        # Conteos
        conteo_anio = contar_por_anio_trimestre_o_mes(df, periodo="anio")
        print("\nConteo por año:")
        print(conteo_anio)

        # conteo_trimestre = contar_por_anio_trimestre_o_mes(df, periodo="trimestre")
        # print("\nConteo por año y trimestre:")
        # print(conteo_trimestre)

        # conteo_mes = contar_por_anio_trimestre_o_mes(df, periodo="mes")
        # print("\nConteo por año y mes:")
        # print(conteo_mes)

        # Tasas de crecimiento
        # tasa_anual = tasa_crecimiento(df, periodo="anio", desde=(2019,), hasta=(2024,))
        # print(f"\nTasa anual 2019 → 2024: {tasa_anual:.2f}%")

        # tasa_trim = tasa_crecimiento(df, periodo="trimestre", desde=(2019, 1), hasta=(2024, 1))
        # print(f"Tasa T1 2019 → T1 2024: {tasa_trim:.2f}%")

        # tasa_mes = tasa_crecimiento(df, periodo="mes", desde=(2019, 1), hasta=(2024, 1))
        # print(f"Tasa enero 2019 → enero 2024: {tasa_mes:.2f}%")

#Ayuda a que no se ejecute automáticamente al importar
if __name__ == "__main__":
    main()
