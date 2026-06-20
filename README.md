# TB4 — Data Visualization · Energía Global

**URL del dashboard en producción:** `https://tb4datavisualization-6nntn6wfsqxza8dx3rpjjx.streamlit.app/`  

## Integrantes
| Control | Ubicación |
|---------|------------|
| Jose Cespedes | U202211884  |
| Jimena Quintana | U20201F576 |
| Rodrigo Gamero | U20231b834 |
| Joaquín Ruiz | U20201F678  |
| Ricardo Tejada | U202113697  |

---

## Descripción

Dashboard interactivo sobre transición energética y sostenibilidad global (2000–2019), construido sobre dos datasets oficiales fusionados:

- **Dataset A** — Our World in Data Energy (OWID): ~200 países, 1965–2024, 130 variables.
- **Dataset B** — Global Data on Sustainable Energy (Kaggle): 176 países × 21 años, variables clave de acceso, renovables, CO₂ e intensidad energética.

Ambos se fusionan por `country + year` generando `data/merged.csv` (17 265 filas × 47 columnas).

---

## Estructura

```
TB4-DataViz/
├── README.md              ← este archivo; primera línea: URL del dashboard
├── requirements.txt       ← dependencias con versión exacta
├── app.py                 ← master del dashboard: sidebar + pestañas por bloque
├── paleta.md              ← validación de accesibilidad de color (Anexo A)
├── data/
│   ├── merge.py                              ← lee los CSV y genera merged.csv
│   ├── owid-energy-data.csv                  ← Dataset A
│   ├── global-data-on-sustainable-energy.csv ← Dataset B
│   └── merged.csv                            ← generado por merge.py
└── blocks/
    ├── __init__.py        ← módulo Python
    ├── data_loader.py     ← carga merged.csv, paleta de colores, base_layout
    ├── bloque_a.py        ← P1, P2, P3
    ├── bloque_b.py        ← P4, P5, P6, P7
    └── bloque_c.py        ← P8, P9
```

---

## Cómo reproducir el dashboard

```bash
# 1. Clonar el repositorio
git clone https://github.com/[usuario]/TB4-DataViz.git
cd TB4-DataViz

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Generar el dataset fusionado
python data/merge.py

# 4. Lanzar el dashboard
streamlit run app.py
```

> Los archivos CSV deben estar en `data/` antes de ejecutar `merge.py`.  
> El script verifica su existencia y lanza un error descriptivo si falta alguno.

---

## Preguntas que responde el dashboard

| Bloque | Pregunta | Tipo de visualización |
|--------|----------|-----------------------|
| A | P1 — Top 15 líderes de la transición renovable (2000→2019) | Barras horizontales — Top 5 en azul, resto en gris |
| A | P2 — Trayectoria regional de intensidad de carbono | Líneas múltiples — mejor en azul, peor en rojo, resto en gris |
| A | P3 — PIB per cápita vs. participación renovable | Scatter plot con escala log y línea de tendencia |
| B | P4 — Pobreza energética y dependencia fósil | Scatter con zona de alarma sombreada (año seleccionable) |
| B | P5 — Consumo energético per cápita: 2000 vs 2019 | Barras horizontales dobles superpuestas |
| B | P6 — Mix eléctrico por fuente | Barra apilada 100% horizontal (país seleccionable) |
| B | P7 — América Latina: cambio en intensidad de carbono | Barras divergentes verde/rojo ordenadas por magnitud |
| C | P8 — Perú vs. promedio América Latina (3 indicadores) | 3 paneles: barra de Perú + línea de promedio LA |
| C | P9 — Perú vs. Chile, Colombia y Brasil | Líneas múltiples — Perú en rojo grueso, resto en gris |
| D | P10 — Defensa de diseño | Argumentación verbal del equipo |

---

## Controles interactivos

| Control | Ubicación | Afecta |
|---------|-----------|--------|
| Slider de año | Sidebar | P3 (scatter) y P4 (scatter zona crítica) |
| Selector de país | Sidebar | P6 (mix eléctrico) |
| Multiselect de regiones | Sidebar | P2 (trayectoria de carbono) |

---

## Decisiones de diseño

- **Sin grids de fondo** en ningún gráfico — fondo blanco limpio.
- **Sin gráficos de torta, donut ni 3D** — restricción absoluta del TB4.
- **Escala logarítmica en P3** — distribuye los 170 países de forma legible dado el rango extremo de PIB (300–105 000 USD).
- **Gris para contexto, color para respuesta** — en P1, P2, P5 y P9 el color de énfasis marca únicamente los elementos relevantes para la pregunta.
- **Perú resaltado en rojo (`#e63946`)** en P8 y P9 para ubicación inmediata.

---

## Paleta de color

Ver [`paleta.md`](paleta.md) — validación completa según Anexo A del TB4.

| Uso | Colores |
|-----|---------|
| Énfasis / mejor | `#1a6faf` (azul) |
| Alerta / peor | `#c0392b` (rojo) |
| Mejora (P7) | `#2ecc71` (verde) |
| Perú | `#e63946` (rojo Perú) |
| Contexto neutro | `#d0d0d0` (gris claro) |
| Tendencia (P3) | `#e67e22` (naranja) |

Todas las paletas validadas como **colorblind safe** en [colorbrewer2.org](https://colorbrewer2.org).
