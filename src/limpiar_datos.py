"""Paso 2 del pipeline: limpiar los datos crudos y calcular resúmenes.

Idea clave: cada fila que entra termina en UNO de dos lugares:
  - en los datos limpios, o
  - en los rechazados, con una columna "motivo" que explica por qué.
Así nunca "perdemos" datos sin saber la razón.
"""

from pathlib import Path

import pandas as pd

# Reglas de rechazo, en el orden en que se aplican.
# Si una fila rompe varias reglas, se queda con el motivo de la primera.
MOTIVO_FECHA = "fecha_invalida"
MOTIVO_PRECIO = "precio_invalido"
MOTIVO_CUERDAS = "cuerdas_invalidas"
MOTIVO_DUPLICADO = "duplicado"
REGLAS = [MOTIVO_FECHA, MOTIVO_PRECIO, MOTIVO_CUERDAS, MOTIVO_DUPLICADO]

COLUMNAS_TEXTO = ["cliente", "municipio", "servicio"]


def normalizar_texto(serie):
    """Quita espacios de más y pone cada palabra con mayúscula inicial.

    Ejemplo: "  isabela " -> "Isabela", "SANTA  ISABEL" -> "Santa Isabel".
    """
    return (
        serie.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)  # varios espacios -> uno
        .str.title()
    )


def convertir_precio(serie):
    """Convierte precios como "$1,200.50" a números (1200.5).

    Lo que no se pueda convertir (vacíos, texto raro) queda como NaN,
    que en pandas significa "valor que falta".
    """
    texto = serie.astype("string").str.replace(r"[$,\s]", "", regex=True)
    return pd.to_numeric(texto, errors="coerce")


def limpiar(df_crudo):
    """Limpia los datos y separa las filas buenas de las rechazadas.

    Devuelve tres cosas:
      - limpios: DataFrame con los datos buenos
      - rechazados: DataFrame con las filas originales + columna "motivo"
      - reporte: diccionario con cuántas filas entraron, salieron y por qué
    """
    df = df_crudo.copy()

    # 1) Arreglar formatos (esto no elimina filas, solo las "pone bonitas").
    for columna in COLUMNAS_TEXTO:
        df[columna] = normalizar_texto(df[columna])
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="coerce")
    df["precio"] = convertir_precio(df["precio"])
    df["cuerdas"] = pd.to_numeric(df["cuerdas"], errors="coerce")

    # 2) Marcar qué filas rompe cada regla.
    #    Cada regla es una "máscara": una lista de True/False por fila.
    #    El duplicado se calcula DESPUÉS de normalizar, así "isabela" e
    #    "Isabela" cuentan como la misma fila. keep="first" conserva la
    #    primera copia y marca solo las repetidas.
    mascaras = {
        MOTIVO_FECHA: df["fecha"].isna(),
        MOTIVO_PRECIO: df["precio"].isna() | (df["precio"] <= 0),
        MOTIVO_CUERDAS: df["cuerdas"].isna() | (df["cuerdas"] <= 0),
        MOTIVO_DUPLICADO: df.duplicated(keep="first"),
    }

    # 3) Asignar a cada fila el motivo de la PRIMERA regla que rompe.
    motivo = pd.Series(pd.NA, index=df.index, dtype="string")
    for regla in REGLAS:
        sin_motivo = motivo.isna()
        motivo[sin_motivo & mascaras[regla]] = regla

    es_rechazada = motivo.notna()

    # Los rechazados se guardan con sus valores ORIGINALES (sin limpiar),
    # para poder ver exactamente qué venía mal.
    rechazados = df_crudo[es_rechazada].copy()
    rechazados["motivo"] = motivo[es_rechazada]
    rechazados = rechazados.reset_index(drop=True)

    limpios = df[~es_rechazada].sort_values("fecha").reset_index(drop=True)

    reporte = {
        "filas_entrada": len(df_crudo),
        "eliminadas_por_regla": {
            regla: int((motivo == regla).sum()) for regla in REGLAS
        },
        "filas_salida": len(limpios),
    }
    return limpios, rechazados, reporte


def formatear_reporte(reporte):
    """Convierte el reporte en un texto fácil de leer."""
    lineas = [
        "=== Reporte de limpieza ===",
        f"Filas que entraron:  {reporte['filas_entrada']}",
        "Filas eliminadas por regla:",
    ]
    for regla, cantidad in reporte["eliminadas_por_regla"].items():
        lineas.append(f"  - {regla:<18} {cantidad}")
    total = sum(reporte["eliminadas_por_regla"].values())
    lineas.append(f"Total eliminadas:    {total}")
    lineas.append(f"Filas que quedaron:  {reporte['filas_salida']}")
    return "\n".join(lineas)


def ingreso_por_mes(limpios):
    """Suma el precio de los servicios de cada mes (formato "2025-01")."""
    meses = limpios["fecha"].dt.to_period("M").astype(str)
    return (
        limpios.groupby(meses)["precio"]
        .sum()
        .round(2)
        .rename_axis("mes")
        .reset_index(name="ingreso")
    )


def ingreso_por_municipio(limpios):
    """Suma el precio por municipio, de mayor a menor ingreso."""
    return (
        limpios.groupby("municipio")["precio"]
        .sum()
        .round(2)
        .sort_values(ascending=False)
        .reset_index(name="ingreso")
    )


def ejecutar(ruta_crudo, carpeta_limpios, ruta_rechazados):
    """Corre todo el paso de limpieza: lee, limpia, imprime y guarda.

    Devuelve el DataFrame de ingreso por mes (lo usa el paso de la gráfica).
    """
    carpeta_limpios = Path(carpeta_limpios)
    ruta_rechazados = Path(ruta_rechazados)
    carpeta_limpios.mkdir(parents=True, exist_ok=True)
    ruta_rechazados.parent.mkdir(parents=True, exist_ok=True)

    df_crudo = pd.read_csv(ruta_crudo)
    limpios, rechazados, reporte = limpiar(df_crudo)
    print(formatear_reporte(reporte))

    por_mes = ingreso_por_mes(limpios)
    por_municipio = ingreso_por_municipio(limpios)

    limpios.to_csv(carpeta_limpios / "servicios_limpios.csv", index=False)
    por_mes.to_csv(carpeta_limpios / "ingreso_por_mes.csv", index=False)
    por_municipio.to_csv(carpeta_limpios / "ingreso_por_municipio.csv", index=False)
    rechazados.to_csv(ruta_rechazados, index=False)

    return por_mes


if __name__ == "__main__":
    ejecutar(
        "data/raw/servicios_drones.csv",
        "data/clean",
        "data/rejected/rechazados.csv",
    )
