# Episodio 003 — D1 vs. tiendas de barrio

## Objetivo

Analizar, con fuentes públicas y evidencia verificable, la relación entre la expansión de las tiendas D1 y las tiendas de barrio en Colombia.

La investigación buscará identificar hallazgos claros para la narrativa del episodio, distinguiendo siempre entre asociaciones observadas y efectos causales demostrados.

## Preguntas iniciales

1. ¿Cómo y dónde se ha expandido D1 en Colombia?
2. ¿Qué caracteriza a las tiendas de barrio y cuál es su papel económico?
3. ¿Qué evidencia existe sobre cambios en precios, empleo, consumo y comercio local?
4. ¿Qué diferencias territoriales o socioeconómicas aparecen en la competencia entre ambos formatos?

## Estructura del proyecto

```text
data/raw/        Datos originales locales y documentación de fuentes.
data/interim/    Datos temporales durante la transformación.
data/processed/  Datasets listos para el análisis.
notebooks/       Exploración, limpieza y análisis reproducible.
src/             Funciones y módulos reutilizables.
outputs/         Gráficos, tablas y resultados generados.
docs/            Notas metodológicas, fuentes y hallazgos.
video/           Materiales para la producción audiovisual.
```

Los datos originales no se versionan. Cada fuente debe documentarse en `data/raw/README.md` con su URL, fecha de descarga, periodo y transformaciones realizadas.
