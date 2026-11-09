# Learning-Claude

Repositorio para aprender y experimentar con Claude y Claude Code.

## Mini pipeline de datos: servicios de drones agrícolas

Un *pipeline* es una cadena de pasos: cada paso recibe datos, los transforma y se los pasa al siguiente.

1. **Generar** (`src/generar_datos.py`): crea `data/raw/servicios_drones.csv` con errores a propósito.
2. **Limpiar y resumir** (`src/limpiar_datos.py`): limpia los datos, imprime un reporte y guarda:
   - `data/clean/servicios_limpios.csv`
   - `data/clean/ingreso_por_mes.csv` y `data/clean/ingreso_por_municipio.csv`
   - `data/rejected/rechazados.csv` (filas rechazadas con la columna `motivo`)
3. **Graficar** (`src/graficar.py`): guarda `output/ingreso_por_mes.png`.

### Cómo usarlo

```bash
pip install -r requirements.txt
python3 main.py      # corre todo el pipeline
python3 -m pytest    # corre las pruebas
```
