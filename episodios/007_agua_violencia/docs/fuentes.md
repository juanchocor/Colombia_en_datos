# Registro inicial de fuentes

Este documento debe actualizarse antes de incorporar una variable al pipeline.

| Dimension | Fuente candidata | Indicador | Unidad | Periodo | Estado |
|---|---|---|---|---|---|
| Cobertura | DANE / fuente oficial de servicios publicos | Cobertura de acueducto | Municipio | Por definir | Por verificar |
| Calidad/riesgo | INS / SIVICAP u otra fuente oficial | Indicador oficial de riesgo | Municipio | Por definir | Por verificar |
| Sin cobertura | Fuente de cobertura seleccionada | Proporcion sin cobertura | Municipio | Por definir | Depende del denominador |
| Contexto conceptual | Galvis Arias, Natalia | Estudio sobre racionamiento en Bogota | Bogota | 2024-2025 | Referencia |

## Ficha obligatoria por fuente

```text
Institucion:
Nombre del dataset:
URL o servicio:
Fecha de consulta:
Periodo de los datos:
Unidad geografica:
Unidad de observacion:
Codigo territorial:
Definicion del indicador:
Variables utilizadas:
Denominador:
Transformaciones:
Limitaciones:
```

No se debe llamar `agua potable` a una variable que solo mida cobertura o riesgo si la fuente no permite esa clasificacion.
