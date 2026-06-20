URL dashboard en producción: pendiente

# TB4 — Data Visualization · Energía Global

## Descripción

Dashboard interactivo construido sobre los datasets:

- **Dataset A** — Our World in Data Energy (OWID): ~200 países, 1965–2024, 130 variables.  
- **Dataset B** — Global Data on Sustainable Energy 2000–2020 (Kaggle): 176 países × 21 años.

Ambos datasets se fusionan mediante `merge` por `country + year`, generando un único archivo
`data/merged.csv` con las columnas necesarias para las preguntas del dashboard.

---

## Estructura

```
TB4-DataViz/
├── README.md              ← este archivo; primera línea: URL del dashboard
├── requirements.txt       ← dependencias con versión exacta
├── app.py                 ← archivo principal del dashboard (Streamlit)
├── paleta.md              ← validación de accesibilidad de color (Anexo A)
└── data/
    ├── merge.py           ← descarga y fusiona los dos datasets → merged.csv
    ├── owid-energy-data.csv        
    ├── global-data-on-sustainable-energy.csv 
    └── merged.csv                  (generado por merge.py)
```

---

## Cómo reproducir el dashboard

```bash
# 1. Clonar el repositorio
git clone https://github.com/[usuario]/TB4-DataViz.git
cd TB4-DataViz

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Descargar y fusionar los datasets
python data/merge.py

# 4. Lanzar el dashboard
streamlit run app.py
```

> El script `data/merge.py` fusiona los CSV locales ubicados en `data/`. Para reproducirlo, coloca `owid-energy-data.csv` y `global-data-on-sustainable-energy.csv` en esa carpeta antes de ejecutarlo.

---

## Preguntas que responde el dashboard

| Bloque | Pregunta | Visualización |
|--------|----------|---------------|
| A | P1 — Líderes de la transición renovable | Slope chart / barras divergentes |
| A | P2 — Trayectoria regional de intensidad de carbono | Líneas múltiples |
| A | P3 — PIB per cápita vs. renovables | Scatter plot |
| B | P4 — Pobreza energética y dependencia fósil | Scatter plot (año seleccionable) |
| B | P5 — Ranking de consumo per cápita 2000–2020 | Bump chart |
| B | P6 — Mix eléctrico por país | Barras apiladas |
| B | P7 — América Latina: cambio en intensidad de carbono | Barras divergentes |
| C | P8 — Perú vs. promedio América Latina | Gráfico multidimensional |
| C | P9 — Perú vs. Chile, Colombia, Brasil | Líneas múltiples |
| D | P10 — Defensa de diseño | Argumentación verbal |

---

## Paleta de color

Ver [`paleta.md`](paleta.md) — validación completa según Anexo A del TB4.  
Paletas usadas: `Set2` (cualitativo), `RdBu` (divergente), `YlOrRd` (secuencial).  
Todas validadas como **colorblind safe** en [colorbrewer2.org](https://colorbrewer2.org).
