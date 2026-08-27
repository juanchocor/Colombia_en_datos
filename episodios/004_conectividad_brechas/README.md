# Episodio: ¿Qué significa estar conectado en Colombia?

## Objetivo

Analizar la brecha digital en Colombia y explorar cómo las diferencias en acceso y uso de internet pueden relacionarse con otras desigualdades territoriales y con las oportunidades que las personas pueden obtener de la tecnología.

El objetivo del episodio no es construir un ranking de departamentos ni realizar una investigación exhaustiva, sino encontrar **3–5 hallazgos con suficiente evidencia para contar una historia clara en redes sociales**.

La pregunta central es:

> **¿Qué cambia en la vida de una persona cuando internet deja de ser una herramienta ocasional y se convierte en parte de su vida cotidiana?**

---

## Hipótesis de trabajo

### H1 — Brecha de acceso

La conectividad en Colombia ha aumentado, pero existen diferencias territoriales importantes, especialmente entre cabeceras y zonas rurales.

### H2 — Brecha de uso

Tener acceso a internet no significa utilizarlo de la misma manera. Las personas pueden presentar diferencias en las actividades que realizan online.

### H3 — Brecha de resultados

Las diferencias digitales pueden estar relacionadas con diferencias en educación, trabajo, ingresos, información y otras oportunidades.

### H4 — Brecha territorial acumulada

Los territorios con menor conectividad pueden presentar simultáneamente otras desventajas socioeconómicas.

### H5 — Capital digital

Las personas no solamente poseen distintos niveles de acceso a tecnología. También poseen diferentes capacidades para convertir ese acceso en recursos, habilidades y oportunidades.

**Importante:** estas hipótesis serán contrastadas con los datos. No se asumirán como verdaderas.

---

# Estructura narrativa

El episodio se organizará alrededor de tres niveles de brecha digital:

### 1. Acceso

**¿Puedes conectarte?**

Variables posibles:

* acceso a internet;
* tipo de conexión;
* ubicación territorial;
* disponibilidad de dispositivos.

### 2. Uso

**¿Qué haces cuando estás conectado?**

Variables posibles:

* educación;
* trabajo;
* búsqueda de información;
* comunicación;
* entretenimiento;
* trámites;
* comercio;
* uso de herramientas digitales;
* uso de inteligencia artificial.

### 3. Resultados

**¿Qué puedes conseguir gracias a esa conexión?**

Variables posibles:

* educación;
* empleo;
* ingresos;
* actividad económica;
* oportunidades;
* acumulación de habilidades.

Esta última dimensión servirá para introducir el concepto de **capital digital**.

---

# Preguntas principales

El análisis se concentrará inicialmente en:

1. ¿Cómo ha evolucionado la conectividad en Colombia?
2. ¿Qué diferencia existe entre cabeceras y zonas rurales?
3. ¿Qué territorios presentan las mayores brechas?
4. ¿Qué cambios han experimentado los territorios con mayor crecimiento de conectividad?
5. ¿La conectividad se relaciona con otras variables socioeconómicas?
6. ¿Las personas conectadas utilizan internet de manera diferente?
7. ¿Existe una diferencia territorial en el uso de herramientas de inteligencia artificial?
8. ¿Podemos encontrar evidencia de que la expansión de la conectividad estuvo acompañada de cambios económicos o sociales?

---

# Caso de cambio territorial

Una parte importante del análisis será buscar un territorio colombiano donde podamos observar un cambio significativo en conectividad durante el periodo estudiado.

La búsqueda seguirá este proceso:

```text
Datos de conectividad
        ↓
Cambio temporal
        ↓
Identificación de territorios relevantes
        ↓
Cruce con indicadores socioeconómicos
        ↓
Análisis estadístico
        ↓
Selección de un caso narrativo
```

El caso será utilizado como **evidencia descriptiva o estadística**, según lo que permitan los datos.

No se atribuirán automáticamente los cambios económicos o sociales a la llegada de internet.

---

# Fuentes prioritarias

Se priorizarán fuentes oficiales y datos públicos:

* DANE
* MinTIC
* DNP
* TerriData
* CRC

También podrán utilizarse investigaciones académicas para contextualizar e interpretar los resultados.

La fuente utilizada para cada variable será documentada en los archivos correspondientes.

---

# Datos

## Datos originales

Los archivos originales descargados de las fuentes oficiales **no se subirán a GitHub**.

Se conservarán localmente en:

```text
data/raw/
```

El directorio `data/raw/` debe estar incluido en `.gitignore`.

El README de esa carpeta deberá documentar:

* fuente;
* nombre del archivo;
* URL;
* fecha de descarga;
* descripción;
* periodo;
* observaciones relevantes.

## Datos procesados

Los datasets utilizados directamente para el análisis se almacenarán en:

```text
data/processed/
```

Estos archivos sí podrán incorporarse al repositorio cuando tengan un tamaño razonable y sean útiles para reproducir el análisis.

Cada dataset procesado debe documentar su relación con los datos originales.

---

# Pipeline de análisis

```text
01. Descarga de fuentes oficiales
        ↓
02. Inspección de archivos
        ↓
03. Limpieza
        ↓
04. Estandarización territorial
        ↓
05. Selección de variables
        ↓
06. Construcción de datasets procesados
        ↓
07. Análisis descriptivo
        ↓
08. Análisis estadístico
        ↓
09. Identificación de hallazgos
        ↓
10. Construcción de gráficos
        ↓
11. Selección del caso narrativo
        ↓
12. Guion del episodio
```

---

# Análisis estadístico

El análisis será exploratorio y estará orientado a identificar relaciones interesantes.

Se podrán utilizar:

* diferencias absolutas;
* diferencias en puntos porcentuales;
* cambios relativos;
* distribuciones;
* correlaciones;
* regresiones;
* comparación entre grupos;
* análisis temporal;
* análisis territorial.

## Regla de interpretación

Una correlación **no será presentada como causalidad**.

Cuando sea posible utilizar evidencia de estudios cuasi-experimentales o diseños que permitan una interpretación causal, estos resultados serán diferenciados claramente de nuestros análisis descriptivos.

---

# Resultados esperados

Al finalizar el análisis se deberán identificar:

### 5 hallazgos principales

Los resultados más importantes encontrados en los datos.

### 3 hallazgos narrativos

Los resultados con mayor potencial para convertirse en contenido audiovisual.

### Gráficos y mapas

Los elementos visuales que permitan explicar los resultados.

### Hipótesis respaldadas

Hipótesis para las cuales encontramos evidencia compatible.

### Hipótesis no respaldadas

Hipótesis para las cuales la evidencia sea insuficiente o contradictoria.

### Afirmaciones que debemos evitar

Conclusiones que los datos no permiten sostener.

---

# Concepto central: capital digital

El concepto de capital digital se introducirá después de mostrar las diferentes brechas.

La idea que se explorará es:

> **No basta con tener acceso a una tecnología. También importa tener los conocimientos, habilidades, recursos y oportunidades necesarios para convertir ese acceso en beneficios.**

El análisis no asumirá que las personas conectadas necesariamente tienen mejores resultados.

Se buscará evidencia de diferencias sistemáticas en:

```text
Acceso
  ↓
Uso
  ↓
Habilidades
  ↓
Oportunidades
  ↓
Resultados
```

---

# Criterio para seleccionar hallazgos

Un resultado solamente será incluido en el episodio si cumple al menos una de estas condiciones:

* presenta una diferencia grande;
* muestra un cambio temporal importante;
* revela una relación inesperada;
* permite visualizar una desigualdad territorial;
* ayuda a explicar una diferencia en oportunidades;
* tiene una interpretación clara para una audiencia no técnica.

No se incluirán estadísticas únicamente porque estén disponibles.

**La historia tendrá prioridad sobre la cantidad de datos.**

---

# Principio del proyecto

Este proyecto no busca demostrar que internet es bueno o malo.

Busca responder una pregunta más concreta:

> **Cuando una parte de Colombia puede incorporar internet a su educación, trabajo, información y relaciones sociales, mientras otra parte tiene un acceso mucho más limitado, ¿qué diferencias aparecen entre esas dos experiencias?**

La investigación partirá de los datos y no de una conclusión predeterminada.
