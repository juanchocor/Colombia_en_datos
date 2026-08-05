# colombia-en-datos

Proyecto para organizar, analizar y producir episodios basados en datos sobre Colombia.

## Estructura

```text
colombia-en-datos/
├── README.md
├── src/
├── tests/
└── episodios/
    ├── 001_embarazo_adolescente/
    ├── 002_ruido_medellin/
    ├── 003_d1_vs_tiendas/
    └── 004_elecciones/
```

## Convencion por episodio

Cada episodio debe seguir esta estructura base:

```text
episodios/<numero>_<tema>/
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
└── video/
```

## Episodios actuales

- `001_embarazo_adolescente`
- `002_ruido_medellin`
- `003_d1_vs_tiendas`
- `004_elecciones`

## Modulos generales

La carpeta `src/` contiene utilidades compartidas para carga, validacion, limpieza, union, estadistica y visualizacion de datos.

La carpeta `tests/` contiene las pruebas base del proyecto.
