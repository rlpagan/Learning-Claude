"""Corre el pipeline completo en orden: generar -> limpiar -> graficar.

Uso:
    python3 main.py
"""

from src.generar_datos import generar_datos, guardar_csv
from src.graficar import graficar_ingreso_mensual
from src.limpiar_datos import ejecutar as limpiar_y_resumir

RUTA_CRUDO = "data/raw/servicios_drones.csv"
CARPETA_LIMPIOS = "data/clean"
RUTA_RECHAZADOS = "data/rejected/rechazados.csv"
RUTA_GRAFICA = "output/ingreso_por_mes.png"


def main():
    print("Paso 1: generando datos crudos...")
    guardar_csv(generar_datos(), RUTA_CRUDO)
    print(f"  -> {RUTA_CRUDO}\n")

    print("Paso 2: limpiando datos y calculando ingresos...")
    por_mes = limpiar_y_resumir(RUTA_CRUDO, CARPETA_LIMPIOS, RUTA_RECHAZADOS)
    print(f"  -> {CARPETA_LIMPIOS}/ y {RUTA_RECHAZADOS}\n")

    print("Paso 3: dibujando la gráfica...")
    graficar_ingreso_mensual(por_mes, RUTA_GRAFICA)
    print(f"  -> {RUTA_GRAFICA}\n")

    print("¡Pipeline terminado!")


if __name__ == "__main__":
    main()
