# Episodio 007 — Agua, violencia y condiciones sociales en Colombia

## Pregunta central

> ¿Qué ocurre cuando la dificultad para acceder a un recurso básico deja de ser un evento temporal y se convierte en una condición permanente del territorio?

El episodio parte del estudio de Natalia Galvis Arias, *Does Urban Water Scarcity Increase Domestic Violence? Evidence from Water Rationing in Bogota*, que analiza los racionamientos temporales de agua en Bogota durante 2024-2025. El estudio no encuentra evidencia de un aumento estadisticamente significativo de la violencia domestica reportada.

Nuestro analisis escala esa pregunta hacia Colombia. No intentamos medir violencia, pobreza o salud como consecuencias directas. Medimos condiciones territoriales de acceso al agua y usamos la literatura existente para discutir por que esas condiciones pueden importar socialmente.

## Alcance

Las tres dimensiones iniciales son:

1. Cobertura de acueducto.
2. Calidad o riesgo del agua, segun el indicador oficial disponible.
3. Ausencia de cobertura, interpretada segun el denominador y la definicion de la fuente.

La unidad territorial principal sera el municipio, siempre que las fuentes sean comparables. Se priorizara el codigo DIVIPOLA.

## Principios metodologicos

- El proyecto es descriptivo y exploratorio.
- Una coincidencia espacial no demuestra causalidad.
- El mecanismo `agua -> tiempo -> tareas -> presion -> relaciones` es una hipotesis narrativa, no un resultado causal de este episodio.
- La denominacion de cada variable seguira la definicion oficial de la fuente.
- Cada fuente debe registrar institucion, URL, fecha de consulta, periodo, unidad geografica y observaciones metodologicas.
- Los datos crudos se conservan sin modificar y no se versionan.

## Estructura

```text
007_agua_violencia/
├── README.md
├── requirements.txt
├── environment.yml
├── .gitignore
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
│   ├── fuentes.md
│   └── metodologia.md
├── notebooks/
├── outputs/
│   ├── figures/
│   └── tables/
├── scripts/
│   ├── 01_fuentes.py
│   ├── 02_cobertura.py
│   ├── 03_calidad.py
│   ├── 04_sin_cobertura.py
│   ├── 05_integracion.py
│   └── 06_resultados.py
├── src/
└── video/
```

## Pipeline

1. `01_fuentes.py`: registra y revisa las fuentes candidatas.
2. `02_cobertura.py`: prepara la cobertura de acueducto.
3. `03_calidad.py`: prepara el indicador oficial de calidad o riesgo.
4. `04_sin_cobertura.py`: construye la ausencia de cobertura cuando la definicion lo permita.
5. `05_integracion.py`: integra las capas mediante DIVIPOLA y valida duplicados y faltantes.
6. `06_resultados.py`: genera tablas, estadisticas descriptivas y exportaciones para visualizacion.

Cada etapa debe ejecutarse despues de documentar y validar sus insumos. Los scripts iniciales crean las carpetas necesarias y sirven como puntos de entrada para el desarrollo posterior.

## Ejecucion

Desde la raiz del repositorio:

```powershell
python episodios/007_agua_violencia/scripts/01_fuentes.py
python episodios/007_agua_violencia/scripts/02_cobertura.py
python episodios/007_agua_violencia/scripts/03_calidad.py
python episodios/007_agua_violencia/scripts/04_sin_cobertura.py
python episodios/007_agua_violencia/scripts/05_integracion.py
python episodios/007_agua_violencia/scripts/06_resultados.py
```

## Fuentes prioritarias

- DANE.
- Superintendencia de Servicios Publicos Domiciliarios y SUI.
- Ministerio de Vivienda.
- Instituto Nacional de Salud y fuentes oficiales de calidad del agua.
- Servicios GIS o APIs oficiales cuando esten disponibles.
- Galvis Arias, Natalia, como estudio conceptual y metodologico de partida.

La lista de fuentes, definiciones y decisiones de comparabilidad se mantiene en [docs/fuentes.md](docs/fuentes.md).
