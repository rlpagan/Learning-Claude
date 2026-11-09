"""Paso 1 del pipeline: generar un CSV de ejemplo con datos "crudos".

Los datos crudos imitan la vida real: vienen con errores a propósito
(espacios de más, mayúsculas mezcladas, precios escritos como texto,
filas duplicadas, valores vacíos, fechas imposibles y cuerdas negativas).
Así el paso de limpieza tiene trabajo de verdad.
"""

import random
from pathlib import Path

import pandas as pd

CLIENTES = [
    "Finca El Cafetal",
    "Hacienda Buena Vista",
    "Agro Lajas",
    "Cosecha Verde",
    "Finca La Esperanza",
    "Platanera Don Luis",
    "Hidropónicos Del Oeste",
    "Granja Monte Alto",
]

MUNICIPIOS = [
    "Isabela",
    "Lajas",
    "Adjuntas",
    "Utuado",
    "Mayagüez",
    "Santa Isabel",
    "Jayuya",
    "Añasco",
]

# Tarifa por cuerda (en dólares) de cada servicio.
TARIFAS = {
    "Fumigación": 35,
    "Siembra": 45,
    "Mapeo": 20,
    "Inspección": 15,
}

# Ningún servicio cuesta menos que este mínimo.
PRECIO_MINIMO = 150


def _ensuciar_texto(texto, rng):
    """Devuelve el texto con algún "error humano" típico (o sin cambios)."""
    opcion = rng.random()
    if opcion < 0.15:
        return texto.lower()
    if opcion < 0.25:
        return texto.upper()
    if opcion < 0.40:
        return f"  {texto} "  # espacios de más al principio y al final
    return texto


def generar_datos(n=200, semilla=42):
    """Crea un DataFrame con `n` servicios, con errores a propósito.

    La `semilla` hace que los números "al azar" sean siempre los mismos,
    así cada vez que corremos el script obtenemos el mismo CSV.
    """
    rng = random.Random(semilla)
    filas = []

    for _ in range(n):
        # Fecha al azar dentro del año 2025.
        fecha = pd.Timestamp("2025-01-01") + pd.Timedelta(days=rng.randint(0, 364))
        servicio = rng.choice(list(TARIFAS))
        cuerdas = round(rng.uniform(1, 60), 1)
        precio = max(PRECIO_MINIMO, round(TARIFAS[servicio] * cuerdas, 2))

        filas.append(
            {
                "fecha": fecha.strftime("%Y-%m-%d"),
                "cliente": _ensuciar_texto(rng.choice(CLIENTES), rng),
                "municipio": _ensuciar_texto(rng.choice(MUNICIPIOS), rng),
                "cuerdas": cuerdas,
                "servicio": _ensuciar_texto(servicio, rng),
                # Algunos precios vienen como texto con "$" y comas.
                "precio": f"${precio:,.2f}" if rng.random() < 0.3 else precio,
            }
        )

    df = pd.DataFrame(filas)

    # --- Errores a propósito ---
    # 1) Precios vacíos.
    for i in rng.sample(range(n), 6):
        df.loc[i, "precio"] = None
    # 2) Cuerdas negativas o en cero (imposible en la vida real).
    for i in rng.sample(range(n), 5):
        df.loc[i, "cuerdas"] = rng.choice([-5.0, -12.5, 0.0])
    # 3) Fechas que no existen.
    for i in rng.sample(range(n), 4):
        df.loc[i, "fecha"] = rng.choice(["2025-13-01", "2025-02-30", "sin fecha"])
    # 4) Filas duplicadas (alguien copió y pegó dos veces).
    duplicados = df.sample(n=8, random_state=semilla)
    df = pd.concat([df, duplicados], ignore_index=True)

    # Barajamos las filas para que los duplicados no queden todos al final.
    return df.sample(frac=1, random_state=semilla).reset_index(drop=True)


def guardar_csv(df, ruta):
    """Guarda el DataFrame como CSV, creando la carpeta si hace falta."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)
    return ruta


if __name__ == "__main__":
    ruta = guardar_csv(generar_datos(), "data/raw/servicios_drones.csv")
    print(f"CSV crudo guardado en {ruta}")
