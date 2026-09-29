# Homogamia étnica en Colombia

## 1. Descripción

Este proyecto busca analizar los patrones de homogamia étnica en las parejas convivientes de distinto sexo en Colombia, utilizando los microdatos del Censo Nacional de Población y Vivienda (CNPV) de 2018 del DANE.

El objetivo es identificar qué proporción de las parejas está conformada por personas que comparten una categoría de autorreconocimiento étnico y explorar cómo varían estos patrones según el sexo y el territorio.

El análisis forma parte de Colombia en Datos.

## 2. Preguntas de investigación

1. ¿Qué proporción de las parejas convivientes de distinto sexo presenta homogamia étnica?
2. ¿Qué proporción de los hombres que se autorreconocen como negros, afrocolombianos, raizales o palenqueros tiene una pareja de la misma categoría étnica?
3. ¿Cómo varían estos patrones según el sexo, el departamento y la composición étnica de la población?

## 3. Fuente de datos

- Entidad: Departamento Administrativo Nacional de Estadística (DANE).
- Operación estadística: Censo Nacional de Población y Vivienda 2018.
- Unidad de análisis: parejas convivientes identificables en los microdatos censales.
- Cobertura: Colombia.

Los archivos descargados están distribuidos por departamentos. Antes de consolidarlos, se verificará que compartan estructura, variables y codificación.

Fuente oficial: https://www.dane.gov.co/

## 4. Alcance y limitaciones

El censo permite estudiar parejas convivientes, incluidas las uniones libres. Los resultados no representan necesariamente todos los matrimonios ni todas las relaciones románticas del país.

La homogamia étnica se medirá mediante el autorreconocimiento étnico registrado en el censo. Esta variable no equivale necesariamente al color de piel percibido por otras personas.

La composición de las parejas no permite inferir directamente las preferencias románticas individuales ni establecer relaciones causales.

## 5. Metodología

1. Inventariar los archivos censales por departamento.
2. Revisar los diccionarios y la estructura de los archivos.
3. Validar los identificadores de vivienda, hogar y persona.
4. Identificar las parejas convivientes y sus integrantes.
5. Verificar las categorías de sexo, parentesco y autorreconocimiento étnico.
6. Validar duplicados, registros faltantes y consistencia de los emparejamientos.
7. Calcular indicadores de homogamia étnica.
8. Desagregar los resultados por sexo y departamento.
9. Exportar tablas y resultados reproducibles.

## 6. Indicadores principales

### Homogamia étnica

Porcentaje de parejas en las que ambos integrantes pertenecen a la misma categoría de autorreconocimiento étnico.

### Homogamia entre parejas con al menos un integrante afrodescendiente

Proporción de parejas en las que ambos integrantes pertenecen a la categoría afrodescendiente definida para el análisis, dentro del universo de parejas con al menos un integrante de dicha categoría.

### Composición de las parejas de hombres afrodescendientes

Porcentaje de hombres afrodescendientes que conviven con una pareja de la misma categoría étnica, dentro del universo de hombres afrodescendientes identificados en parejas convivientes.

Los denominadores y las categorías étnicas se documentarán explícitamente antes de calcular los indicadores.

## 7. Estructura del proyecto

```text
008_Homogamia/
├── data/
│   ├── raw/
│   │   └── censo_2018/
│   │       ├── departamento_01/
│   │       ├── departamento_02/
│   │       └── ...
│   ├── interim/
│   └── processed/
├── scripts/
│   ├── 01_inventario.py
│   ├── 02_validacion.py
│   ├── 03_consolidacion.py
│   ├── 04_identificacion_parejas.py
│   ├── 05_indicadores.py
│   └── 06_resultados.py
├── outputs/
│   ├── tables/
│   └── figures/
├── docs/
│   ├── fuentes.md
│   └── metodologia.md
├── notebooks/
├── src/
├── video/
├── requirements.txt
├── environment.yml
└── .gitignore
```

La estructura definitiva dependerá de los formatos y archivos descargados.

## 8. Reproducibilidad

- Mantener los archivos originales sin modificaciones.
- No publicar microdatos personales.
- Documentar las transformaciones y decisiones metodológicas.
- Registrar las categorías y los denominadores utilizados.
- Validar los resultados antes de generar visualizaciones.
- Evitar incluir los microdatos originales en Git.

## 9. Estado del proyecto

- [x] Identificación de la fuente censal.
- [x] Identificación de la distribución territorial de los archivos.
- [ ] Inventario de archivos y formatos.
- [ ] Revisión del diccionario de variables.
- [ ] Validación de identificadores.
- [ ] Identificación de parejas convivientes.
- [ ] Cálculo de indicadores.
- [ ] Análisis territorial.
- [ ] Documentación de resultados.

## Ejecución

Desde la raíz del repositorio:

```powershell
python episodios/008_Homogamia/scripts/01_inventario.py
python episodios/008_Homogamia/scripts/02_validacion.py
python episodios/008_Homogamia/scripts/03_consolidacion.py
python episodios/008_Homogamia/scripts/04_identificacion_parejas.py
python episodios/008_Homogamia/scripts/05_indicadores.py
python episodios/008_Homogamia/scripts/06_resultados.py
```