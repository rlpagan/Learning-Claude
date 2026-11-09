"""Paso 3 del pipeline: dibujar el ingreso por mes y guardarlo como PNG."""

from pathlib import Path

import matplotlib

# "Agg" dibuja directo a un archivo, sin abrir ventanas.
# Así el script funciona también en servidores sin pantalla.
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

COLOR_BARRA = "#2a78d6"
COLOR_TEXTO = "#52514e"
COLOR_REJILLA = "#e4e3df"


def graficar_ingreso_mensual(por_mes, ruta_png):
    """Gráfica de barras: un mes por barra, altura = ingreso del mes."""
    ruta_png = Path(ruta_png)
    ruta_png.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    ax.bar(por_mes["mes"], por_mes["ingreso"], color=COLOR_BARRA, width=0.6)

    # Etiqueta solo el mes con más ingreso (un número en cada barra satura).
    fila_max = por_mes.loc[por_mes["ingreso"].idxmax()]
    ax.annotate(
        f"${fila_max['ingreso']:,.0f}",
        (fila_max["mes"], fila_max["ingreso"]),
        textcoords="offset points",
        xytext=(0, 4),
        ha="center",
        color=COLOR_TEXTO,
        fontsize=9,
    )

    ax.set_title("Ingreso por mes – servicios de drones agrícolas", loc="left")
    ax.set_ylabel("Ingreso (USD)", color=COLOR_TEXTO)
    ax.yaxis.set_major_formatter(lambda valor, _pos: f"${valor:,.0f}")
    ax.tick_params(colors=COLOR_TEXTO, labelsize=9)
    ax.tick_params(axis="x", rotation=45)

    # Rejilla suave detrás de las barras y sin bordes innecesarios.
    ax.grid(axis="y", color=COLOR_REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)

    fig.tight_layout()
    fig.savefig(ruta_png)
    plt.close(fig)  # libera la memoria de la figura
    return ruta_png


if __name__ == "__main__":
    import pandas as pd

    datos = pd.read_csv("data/clean/ingreso_por_mes.csv")
    print(f"Gráfica guardada en {graficar_ingreso_mensual(datos, 'output/ingreso_por_mes.png')}")
