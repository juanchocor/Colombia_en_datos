# Episodio 005 — Pruebas PISA

## Objetivo

Analizar el desempeño de Colombia en las pruebas PISA y explorar qué factores se asocian con resultados educativos, desigualdades de aprendizaje y diferencias territoriales o socioeconómicas.

La investigación buscará responder una pregunta clara: ¿qué nos dicen las pruebas PISA sobre la calidad de la educación y las brechas que aún persisten en el país?

## Preguntas iniciales

1. ¿Cómo se ubica Colombia en comparación con otros países y con su propio desempeño histórico?
2. ¿Qué diferencias existen entre regiones, niveles socioeconómicos y tipos de institución?
3. ¿Qué variables están asociadas con mejor o peor rendimiento en lectura, matemáticas y ciencias?
4. ¿Qué patrones muestran las brechas en acceso, contexto escolar y condiciones de aprendizaje?
5. ¿Qué hallazgos pueden contar una historia clara y verificable para una narrativa de divulgación?

## Estructura del proyecto

```text
005_pruebas_pisa/
├── README.md
├── requirements.txt
├── environment.yml
├── .gitignore
├── LICENSE
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── notebooks/
├── src/
├── outputs/
├── docs/
├── video/
└── .gitkeep
```

## Fuentes y enfoque

Este episodio prioriza fuentes públicas y datos abiertos con metodologías transparentes. Las fuentes pueden incluir:

- OECD / PISA
- MEN / ICFES
- DANE
- datos territoriales y socioeconómicos de Colombia
- documentación metodológica de las bases utilizadas

Toda fuente se documentará con su nombre, enlace, fecha de descarga y observaciones relevantes.

## Datos

### Datos originales

Los archivos fuente de origen no se versionarán en GitHub. Se conservan localmente en:

```text
data/raw/
```

Cada archivo debe documentarse en `data/raw/README.md` con:

- nombre del archivo;
- fuente;
- URL o referencia;
- fecha de descarga;
- periodo cubierto;
- descripción;
- observaciones relevantes.

### Datos procesados

Los datasets limpios y analíticos se almacenarán en:

```text
data/processed/
```

Estos archivos pueden incluirse en el repositorio cuando sean útiles para reproducir el análisis o para compartir resultados.

## Pipeline sugerido

```text
01. Revisión de fuentes y bases disponibles
        ↓
02. Selección de variables relevantes
        ↓
03. Limpieza y validación de datos
        ↓
04. Construcción de datasets intermedios
        ↓
05. Análisis exploratorio
        ↓
06. Cruce con indicadores socioeconómicos y territoriales
        ↓
07. Identificación de hallazgos
        ↓
08. Construcción de visualizaciones
        ↓
09. Redacción de conclusiones y limitaciones
        ↓
10. Preparación del guion de divulgación
```

## Principios metodológicos

- La evidencia guía la narrativa.
- Las correlaciones no implican causalidad.
- Cada afirmación debe estar respaldada por datos.
- Las limitaciones del análisis se documentan explícitamente.
- Los resultados deben ser reproducibles.

## Recomendación inicial

El trabajo de este episodio debe comenzar con:

1. revisar la estructura de las bases PISA;
2. identificar variables clave de rendimiento y contexto;
3. construir una primera exploración descriptiva;
4. definir 3 a 5 hallazgos con capacidad narrativa.
