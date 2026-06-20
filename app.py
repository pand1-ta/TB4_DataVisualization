"""
app.py — TB4 Data Visualization
Dashboard master: configura sidebar e importa los bloques.
Ejecutar con: streamlit run app.py
"""

import streamlit as st
from blocks.data_loader import load_data
from blocks.bloque_a import render as render_a
from blocks.bloque_b import render as render_b
from blocks.bloque_c import render as render_c

st.set_page_config(
    page_title="TB4 · Energía Global",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

df_full, df_main = load_data()

# ─── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.title("TB4 · Energía Global")
st.sidebar.markdown("---")

year_sel = st.sidebar.slider(
    "Año (P3 y P4)", min_value=2000, max_value=2019, value=2015, step=1,
)

paises_disponibles = sorted(df_main["country"].unique())
pais_sel = st.sidebar.selectbox(
    "País — mix eléctrico (P6)",
    options=paises_disponibles,
    index=paises_disponibles.index("Peru") if "Peru" in paises_disponibles else 0,
)

regiones_todas = sorted(df_main["region"].unique())
regiones_sel = st.sidebar.multiselect(
    "Regiones (P2)", options=regiones_todas, default=regiones_todas,
)

st.sidebar.markdown("---")
st.sidebar.caption("Fuentes: OWID Energy Data · Global Data on Sustainable Energy 2000–2020 (Kaggle)")

params = {
    "year_sel":     year_sel,
    "pais_sel":     pais_sel,
    "regiones_sel": regiones_sel,
}

# ─── Contenido ────────────────────────────────────────────────────────────────

st.title("Energía Global — TB4 Data Visualization")
st.markdown("Dashboard interactivo sobre transición energética y sostenibilidad (2000–2019).")

tab_a, tab_b, tab_c = st.tabs([
    "Bloque A — Panorama global",
    "Bloque B — Patrones y comparaciones",
    "Bloque C — Posición de Perú",
])

with tab_a:
    render_a(df_main, params)

with tab_b:
    render_b(df_main, params)

with tab_c:
    render_c(df_main, params)