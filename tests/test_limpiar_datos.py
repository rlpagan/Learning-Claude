"""Pruebas del paso de limpieza.

Usamos datos pequeños hechos a mano: así sabemos de antemano cuál
debe ser el resultado correcto y podemos comprobarlo.
"""

import pandas as pd
import pytest

from src.generar_datos import generar_datos
from src.limpiar_datos import (
    REGLAS,
    convertir_precio,
    ejecutar,
    formatear_reporte,
    ingreso_por_mes,
    ingreso_por_municipio,
    limpiar,
    normalizar_texto,
)


@pytest.fixture
def df_crudo():
    """7 filas: 3 buenas y 4 malas (una por cada regla)."""
    return pd.DataFrame(
        {
            "fecha": [
                "2025-01-10",  # buena
                "2025-01-20",  # buena
                "2025-02-05",  # buena
                "2025-13-01",  # fecha imposible
                "2025-02-07",  # precio vacío
                "2025-02-08",  # cuerdas negativas
                "2025-01-10",  # duplicado de la primera (con otro formato)
            ],
            "cliente": ["Agro Lajas", "Cosecha Verde", "Agro Lajas", "X", "Y", "Z", "  AGRO LAJAS"],
            "municipio": ["Lajas", " isabela ", "LAJAS", "Lajas", "Lajas", "Lajas", "lajas"],
            "cuerdas": [10, 5, 20, 3, 4, -5, 10],
            "servicio": ["Mapeo", "siembra", "Mapeo", "Mapeo", "Mapeo", "Mapeo", "MAPEO"],
            "precio": ["200", "$1,250.50", 400, 100, None, 100, "$200.00"],
        }
    )


# --- Funciones pequeñas ---

def test_normalizar_texto_quita_espacios_y_arregla_mayusculas():
    serie = pd.Series(["  isabela ", "SANTA  ISABEL", "Añasco"])
    assert list(normalizar_texto(serie)) == ["Isabela", "Santa Isabel", "Añasco"]


def test_convertir_precio_entiende_texto_con_dolar_y_comas():
    serie = pd.Series(["$1,250.50", "300", 99.5, None, "gratis"])
    resultado = convertir_precio(serie)
    assert list(resultado[:3]) == [1250.50, 300.0, 99.5]
    assert resultado[3:].isna().all()


# --- Limpieza completa ---

def test_limpiar_conserva_solo_las_filas_buenas(df_crudo):
    limpios, _, _ = limpiar(df_crudo)
    assert len(limpios) == 3
    assert set(limpios["municipio"]) == {"Lajas", "Isabela"}
    assert limpios["precio"].tolist() == [200.0, 1250.50, 400.0]


def test_cada_fila_termina_en_limpios_o_en_rechazados(df_crudo):
    limpios, rechazados, _ = limpiar(df_crudo)
    assert len(limpios) + len(rechazados) == len(df_crudo)


# --- Rechazados ---

def test_rechazados_tienen_columna_motivo_correcta(df_crudo):
    _, rechazados, _ = limpiar(df_crudo)
    assert "motivo" in rechazados.columns
    assert sorted(rechazados["motivo"]) == sorted(REGLAS)


def test_rechazados_guardan_los_valores_originales(df_crudo):
    _, rechazados, _ = limpiar(df_crudo)
    duplicado = rechazados[rechazados["motivo"] == "duplicado"].iloc[0]
    # El valor original sin limpiar, para ver qué venía mal.
    assert duplicado["cliente"] == "  AGRO LAJAS"


def test_fila_con_varios_errores_usa_el_motivo_de_la_primera_regla():
    df = pd.DataFrame(
        {
            "fecha": ["no es fecha"],
            "cliente": ["A"],
            "municipio": ["Lajas"],
            "cuerdas": [-1],  # también rompe la regla de cuerdas
            "servicio": ["Mapeo"],
            "precio": [None],  # y la de precio
        }
    )
    _, rechazados, reporte = limpiar(df)
    assert rechazados["motivo"].tolist() == ["fecha_invalida"]
    assert sum(reporte["eliminadas_por_regla"].values()) == 1


# --- Reporte ---

def test_reporte_cuenta_entrada_salida_y_cada_regla(df_crudo):
    _, _, reporte = limpiar(df_crudo)
    assert reporte["filas_entrada"] == 7
    assert reporte["filas_salida"] == 3
    assert reporte["eliminadas_por_regla"] == {
        "fecha_invalida": 1,
        "precio_invalido": 1,
        "cuerdas_invalidas": 1,
        "duplicado": 1,
    }


def test_reporte_cuadra_con_los_datos_generados():
    """Con el CSV grande de ejemplo, las cuentas también deben cuadrar."""
    df = generar_datos()
    limpios, rechazados, reporte = limpiar(df)
    eliminadas = sum(reporte["eliminadas_por_regla"].values())
    assert reporte["filas_entrada"] == reporte["filas_salida"] + eliminadas
    assert eliminadas == len(rechazados)
    assert reporte["filas_salida"] == len(limpios)
    assert all(reporte["eliminadas_por_regla"][regla] > 0 for regla in REGLAS)


def test_formatear_reporte_muestra_todas_las_cifras(df_crudo):
    _, _, reporte = limpiar(df_crudo)
    texto = formatear_reporte(reporte)
    assert "Filas que entraron:  7" in texto
    assert "Filas que quedaron:  3" in texto
    assert "Total eliminadas:    4" in texto
    for regla in REGLAS:
        assert regla in texto


def test_ejecutar_imprime_el_reporte_y_guarda_archivos(df_crudo, tmp_path, capsys):
    """Prueba de punta a punta usando una carpeta temporal."""
    ruta_crudo = tmp_path / "crudo.csv"
    df_crudo.to_csv(ruta_crudo, index=False)
    ruta_rechazados = tmp_path / "rejected" / "rechazados.csv"

    ejecutar(ruta_crudo, tmp_path / "clean", ruta_rechazados)

    assert "Reporte de limpieza" in capsys.readouterr().out
    assert (tmp_path / "clean" / "servicios_limpios.csv").exists()
    guardados = pd.read_csv(ruta_rechazados)
    assert len(guardados) == 4
    assert "motivo" in guardados.columns


# --- Resúmenes de ingreso ---

def test_ingreso_por_mes(df_crudo):
    limpios, _, _ = limpiar(df_crudo)
    resultado = ingreso_por_mes(limpios)
    assert resultado.to_dict("records") == [
        {"mes": "2025-01", "ingreso": 1450.50},
        {"mes": "2025-02", "ingreso": 400.0},
    ]


def test_ingreso_por_municipio_ordenado_de_mayor_a_menor(df_crudo):
    limpios, _, _ = limpiar(df_crudo)
    resultado = ingreso_por_municipio(limpios)
    assert resultado.to_dict("records") == [
        {"municipio": "Isabela", "ingreso": 1250.50},
        {"municipio": "Lajas", "ingreso": 600.0},
    ]
