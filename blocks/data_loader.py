"""
blocks/data_loader.py
Carga merged.csv y expone el DataFrame y las constantes de paleta
que usan todos los bloques.
"""

import os
import streamlit as st
import pandas as pd

# ─── Rutas ───────────────────────────────────────────────────────────────────

# __file__ está en blocks/, subimos un nivel para llegar a la raíz
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_MERGED = os.path.join(ROOT_DIR, "data", "merged.csv")

# ─── Paleta de colores (colorblind safe — ver paleta.md) ─────────────────────

COLORS_REGION = {
    "América Latina":            "#66c2a5",
    "Europa":                    "#fc8d62",
    "Asia-Pacífico":             "#8da0cb",
    "América del Norte":         "#e78ac3",
    "Asia del Sur":              "#a6d854",
    "Medio Oriente y N. África": "#ffd92f",
    "África Subsahariana":       "#e5c494",
    "Asia Central":              "#b3b3b3",
    "Otras regiones":            "#b3b3b3",
}

COLOR_PERU   = "#e63946"   # Perú siempre destacado en rojo
COLOR_MEJORA = "#2166ac"   # Divergente: mejora  (azul)
COLOR_EMPEORA = "#d6604d"  # Divergente: empeora (rojo)

# Colores fijos para vecinos de Perú (P9)
COLORS_VECINOS = {
    "Peru":     COLOR_PERU,
    "Chile":    "#2166ac",
    "Colombia": "#66c2a5",
    "Brazil":   "#ffd92f",
}

# ─── Layout base para todos los gráficos ─────────────────────────────────────

def base_layout(**kwargs) -> dict:
    """
    Devuelve un dict de layout con fondo blanco y sin grids.
    Acepta kwargs para sobreescribir o añadir propiedades.
    """
    layout = dict(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
    )
    layout.update(kwargs)
    return layout


# ─── Carga de datos ───────────────────────────────────────────────────────────

@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retorna dos DataFrames:
      - df_full : todo el merged (1900–2025), útil para P5/P9 con OWID
      - df_main : filtrado 2000–2019, rango principal del TB4
    
    Se usa 2019 como año máximo porque renewable_share_total_energy
    (Dataset B / Kaggle) solo tiene cobertura completa hasta 2019.
    """
    if not os.path.exists(PATH_MERGED):
        st.error(
            "No se encontró `data/merged.csv`. "
            "Ejecuta primero: `python data/merge.py`"
        )
        st.stop()

    df_full = pd.read_csv(PATH_MERGED, low_memory=False)
    df_main = df_full[
        (df_full["year"] >= 2000) & (df_full["year"] <= 2019)
    ].copy()

    return df_full, df_main