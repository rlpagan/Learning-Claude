# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Learning-Claude is a repository for learning and experimenting with Claude and Claude Code. It contains a mini data pipeline (Python 3 + pandas + matplotlib) for agricultural drone services.

## Commands

- Install dependencies: `pip install -r requirements.txt`
- Run the whole pipeline: `python3 main.py`
- Run the tests: `python3 -m pytest` (config in `pytest.ini`, which adds the repo root to `pythonpath`)
- Run a single test: `python3 -m pytest tests/test_limpiar_datos.py::test_ingreso_por_mes`

## Architecture

`main.py` runs three steps in order:

1. `src/generar_datos.py` writes a synthetic CSV with deliberate errors to `data/raw/servicios_drones.csv` (fixed seed, so output is reproducible).
2. `src/limpiar_datos.py` normalizes text, prices and dates, then applies rejection rules in order (`REGLAS`: invalid date, invalid price, invalid cuerdas, duplicate). Each row ends up either in `data/clean/` or in `data/rejected/rechazados.csv` with its original values plus a `motivo` column (first rule broken). `limpiar()` returns `(limpios, rechazados, reporte)`; the report is printed by `ejecutar()`. It also writes monthly and per-municipality revenue CSVs to `data/clean/`.
3. `src/graficar.py` saves a bar chart of monthly revenue to `output/ingreso_por_mes.png`.

Tests live in `tests/` and use small hand-built DataFrames.

## Conventions

- The README and commit messages are written in Spanish; keep user-facing documentation in Spanish unless asked otherwise.
- The default branch is `main`.
- The GitHub repository name is `rlpagan/Learning-Claude` (capital L and C). Using the lowercase URL works but GitHub prints a "This repository moved" warning on push; prefer the correctly cased remote URL.

## Cómo trabajar conmigo

- Estoy aprendiendo data engineering. Explícame cada concepto nuevo con palabras simples.
- Antes de escribir código, muéstrame un plan corto y espera mi aprobación.
- Usa Python 3. Datos crudos en `data/raw` y procesados en `data/clean`.
- Comenta el código en español.
- Al terminar cada tarea, dame 1 o 2 ejercicios para practicar yo mismo.
