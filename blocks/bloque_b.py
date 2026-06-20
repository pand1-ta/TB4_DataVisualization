"""
blocks/bloque_b.py
Bloque B — Patrones y comparaciones
  P4: Scatter acceso electricidad vs. dependencia fósil (año seleccionable)
  P5: Bump chart ranking consumo per cápita 2000–2019
  P6: Mix eléctrico por fuente para el país seleccionado (año de mayor renovable)
  P7: Barras divergentes — cambio en intensidad de carbono en América Latina
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from blocks.data_loader import COLORS_REGION, COLOR_PERU, base_layout

COLOR_TOP    = "#1a6faf"   # azul énfasis
COLOR_WORST  = "#c0392b"   # rojo énfasis
COLOR_GREY   = "#c8c8c8"   # gris neutro
COLOR_OK     = "#1a6faf" 
COLOR_MEJORA  = "#1a6faf"  # azul — redujo carbono
COLOR_EMPEORA = "#c0392b"  # rojo — aumentó carbono

# Colores por fuente eléctrica (intuitivos + colorblind safe)
FUEL_COLORS = {
    "Carbón":    "#4d4d4d",
    "Gas":       "#f28e2b",
    "Nuclear":   "#76b7b2",
    "Solar":     "#edc948",
    "Eólica":    "#59a14f",
    "Hidro":     "#4e79a7",
    "Petróleo":  "#9c755f",
    "Biocomb.":  "#bab0ac",
    "Otras R.":  "#b07aa1",
}


# ─── P4 — Scatter: acceso electricidad vs. dependencia fósil ─────────────────

def _p4_scatter(df: pd.DataFrame, year_sel: int) -> go.Figure:
    """
    Eje X: acceso a electricidad (%).
    Eje Y: % electricidad de origen fósil (100 - low_carbon_elec_pct).
    Cuadrante de interés: acceso < 50% y alta dependencia fósil.
    """
    df_p4 = (
        df[df["year"] == year_sel]
        .dropna(subset=["access_to_electricity", "low_carbon_elec_pct"])
        .copy()
    )
    df_p4["fossil_elec_pct"] = 100 - df_p4["low_carbon_elec_pct"]

    # Clasificar cuadrante de interés
    df_p4["destacado"] = (df_p4["access_to_electricity"] < 50)

    fig = go.Figure()

    # Puntos fuera del cuadrante de interés (gris)
    resto = df_p4[~df_p4["destacado"]]
    fig.add_trace(go.Scatter(
        x=resto["access_to_electricity"],
        y=resto["fossil_elec_pct"],
        mode="markers",
        name="Acceso ≥ 50%",
        marker=dict(color=COLOR_GREY, size=7, opacity=0.6),
        hovertemplate=(
            "<b>%{customdata}</b><br>"
            "Acceso: %{x:.1f}%<br>"
            "Fósil en electricidad: %{y:.1f}%<extra></extra>"
        ),
        customdata=resto["country"],
    ))

    # Puntos en cuadrante de interés (coloreados por región)
    interés = df_p4[df_p4["destacado"]]
    for region in interés["region"].unique():
        sub = interés[interés["region"] == region]
        fig.add_trace(go.Scatter(
            x=sub["access_to_electricity"],
            y=sub["fossil_elec_pct"],
            mode="markers",
            name=region,
            marker=dict(
                color=COLORS_REGION.get(region, "#aaa"),
                size=11,
                opacity=0.9,
                line=dict(color="white", width=0.8),
            ),
            hovertemplate=(
                "<b>%{customdata}</b><br>"
                "Acceso: %{x:.1f}%<br>"
                "Fósil en electricidad: %{y:.1f}%<extra></extra>"
            ),
            customdata=sub["country"],
        ))

    # Línea vertical en umbral 50%
    fig.add_vline(
        x=50, line_dash="dash", line_color="#e74c3c", line_width=2,
        annotation_text="<b>Umbral 50% acceso</b>",
        annotation_position="top right",
        annotation_font_color="#e74c3c",
    )

    # Sombreado cuadrante de interés
    fig.add_vrect(
        x0=0, x1=50,
        fillcolor="#ffecec", opacity=0.3,
        layer="below", line_width=0,
    )

    n_paises = len(interés)
    fig.update_layout(
        title=(
            f"Pobreza energética y dependencia fósil ({year_sel})"
            f" — {n_paises} países con acceso < 50%"
        ),
        xaxis=dict(title="Acceso a electricidad (%)", range=[-2, 102], ticksuffix="%", showgrid=False),
        yaxis=dict(title="Electricidad de origen fósil (%)", range=[-2, 105], ticksuffix="%", showgrid=False),
        height=500,
        legend=dict(title="Región", orientation="v"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=40, t=70, b=50),
    )
    return fig


# ─── P5 ───────────────────────────────────────────────────────────────────────
 
def _p5(df: pd.DataFrame) -> go.Figure:
    """
    Barras horizontales dobles: consumo energético per cápita en 2000 vs 2019.
    Top 12 países por valor en 2019, ordenados de mayor a menor.
    """
    pop_avg = df.groupby("country")["population"].mean()
    paises_grandes = pop_avg[pop_avg > 1_000_000].index.tolist()
 
    df_p5 = df[
        df["country"].isin(paises_grandes) &
        df["year"].isin([2000, 2019])
    ].dropna(subset=["energy_per_capita"]).copy()
 
    # Top 12 por valor en 2019
    top12 = (
        df_p5[df_p5["year"] == 2019]
        .nlargest(12, "energy_per_capita")["country"]
        .tolist()
    )
 
    df_p5 = df_p5[df_p5["country"].isin(top12)].copy()
 
    val2000 = df_p5[df_p5["year"] == 2000].set_index("country")["energy_per_capita"]
    val2019 = df_p5[df_p5["year"] == 2019].set_index("country")["energy_per_capita"]
 
    # Ordenar por valor 2019 descendente
    orden = val2019.sort_values(ascending=True).index.tolist()
 
    fig = go.Figure()
 
    fig.add_trace(go.Bar(
        y=orden,
        x=[val2000.get(c, 0) for c in orden],
        orientation="h",
        name="2000",
        marker_color=COLOR_GREY,
        hovertemplate="<b>%{y}</b><br>2000: %{x:,.0f} kWh/persona<extra></extra>",
    ))
 
    fig.add_trace(go.Bar(
        y=orden,
        x=[val2019.get(c, 0) for c in orden],
        orientation="h",
        name="2019",
        marker_color=COLOR_OK,
        hovertemplate="<b>%{y}</b><br>2019: %{x:,.0f} kWh/persona<extra></extra>",
    ))
 
    fig.update_layout(
        barmode="overlay",
        title="Consumo energético per cápita — Top 12 países (2000 vs 2019)",
        xaxis=dict(title="kWh por persona", showgrid=False),
        yaxis=dict(title="", showgrid=False),
        height=460,
        legend=dict(orientation="h", y=1.06, x=0),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=160, r=40, t=60, b=50),
    )
    return fig


# ─── P6 — Mix eléctrico por fuente ───────────────────────────────────────────

def _p6_mix(df: pd.DataFrame, pais_sel: str) -> go.Figure:
    """
    Barras apiladas del mix de generación eléctrica por fuente (2000–2019).
    Marca el año de mayor producción renovable con una línea vertical.
    """
    fuel_map = {
        "Carbón":    "coal_electricity",
        "Gas":       "gas_electricity",
        "Nuclear":   "nuclear_electricity",
        "Solar":     "solar_electricity",
        "Eólica":    "wind_electricity",
        "Hidro":     "hydro_electricity",
        "Petróleo":  "oil_electricity",
        "Biocomb.":  "biofuel_electricity",
        "Otras R.":  "other_renewable_electricity",
    }
    fuel_exist = {k: v for k, v in fuel_map.items() if v in df.columns}

    df_p6 = (
        df[df["country"] == pais_sel]
        [["year", "renewables_electricity"] + list(fuel_exist.values())]
        .dropna(subset=list(fuel_exist.values()), how="all")
        .copy()
    )

    if df_p6.empty:
        return go.Figure().update_layout(
            title=f"Sin datos de mix eléctrico para {pais_sel}"
        )

    # Año de mayor producción renovable
    df_renew = df_p6.dropna(subset=["renewables_electricity"])
    año_max = int(df_renew.loc[df_renew["renewables_electricity"].idxmax(), "year"])

    fig = go.Figure()

    for fuente, col in fuel_exist.items():
        vals = df_p6.set_index("year")[col].fillna(0)
        fig.add_trace(go.Bar(
            x=vals.index,
            y=vals.values,
            name=fuente,
            marker_color=FUEL_COLORS.get(fuente, "#aaa"),
            hovertemplate=(
                f"<b>{fuente}</b><br>"
                "Año: %{x}<br>"
                "%{y:.1f} TWh<extra></extra>"
            ),
        ))

    # Línea en año de mayor renovable
    fig.add_vline(
        x=año_max,
        line_dash="dash", line_color="#e63946", line_width=2,
        annotation_text=f"<b>Máx. renovable: {año_max}</b>",
        annotation_position="top",
        annotation_font_color="#e63946",
    )

    fig.update_layout(
        barmode="stack",
        title=f"Mix de generación eléctrica — {pais_sel} (2000–2019)",
        xaxis=dict(title="Año", dtick=2, showgrid=False),
        yaxis=dict(title="Generación (TWh)", showgrid=False),
        legend=dict(title="Fuente", orientation="v"),
        height=480,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=40, t=70, b=50),
    )
    return fig


# ─── P7 — Barras divergentes: AL intensidad de carbono ───────────────────────

def _p7_divergente(df: pd.DataFrame) -> go.Figure:
    """
    Barras horizontales divergentes con todos los países de América Latina.
    Azul = mejora (redujo carbono), Rojo = empeora (aumentó carbono).
    Perú destacado con borde negro.
    """
    la = df[df["region"] == "América Latina"]
    piv = (
        la[la["year"].isin([2000, 2019])]
        .pivot_table(index="country", columns="year", values="carbon_intensity_elec")
        .dropna()
    )
    piv.columns = ["y2000", "y2019"]
    piv["delta"] = piv["y2019"] - piv["y2000"]
    piv = piv.sort_values("delta", ascending=True).reset_index()

    colors = [
        COLOR_MEJORA if d < 0 else COLOR_EMPEORA
        for d in piv["delta"]
    ]

    fig = go.Figure(go.Bar(
        x=piv["delta"],
        y=piv["country"],
        orientation="h",
        marker=dict(color=colors),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Cambio: %{x:+.1f} gCO₂/kWh<br>"
            "2000: %{customdata[0]:.1f} | 2019: %{customdata[1]:.1f}<extra></extra>"
        ),
        customdata=piv[["y2000", "y2019"]].values,
    ))

    fig.add_vline(x=0, line_color="#555", line_width=1.5)

    # Etiquetas de valor
    for _, row in piv.iterrows():
        signo = "+" if row["delta"] > 0 else ""
        fig.add_annotation(
            x=row["delta"] + (1 if row["delta"] >= 0 else -1),
            y=row["country"],
            text=f"{signo}{row['delta']:.0f}",
            xanchor="left" if row["delta"] >= 0 else "right",
            showarrow=False,
            font=dict(size=10, color=COLOR_EMPEORA if row["delta"] > 0 else COLOR_MEJORA),
        )

    n_mejora  = (piv["delta"] < 0).sum()
    n_empeora = (piv["delta"] > 0).sum()

    fig.update_layout(
        title=(
            f"Cambio en intensidad de carbono eléctrica — América Latina (2000 → 2019)<br>"
            f"<sup>{n_mejora} países mejoraron (azul) · {n_empeora} empeoraron (rojo)</sup>"
        ),
        xaxis=dict(title="Δ gCO₂/kWh (negativo = mejora)", zeroline=False, showgrid=False),
        yaxis=dict(title="", showgrid=False),
        height=620,
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=140, r=60, t=80, b=50),
    )
    return fig


# ─── Render principal ─────────────────────────────────────────────────────────

def render(df_main: pd.DataFrame, params: dict) -> None:
    st.header("Bloque B — Patrones y comparaciones")

    # ── P4 ────────────────────────────────────────────────────────────────────
    st.subheader(f"P4 · Pobreza energética y dependencia fósil — {params['year_sel']}")
    st.caption(
        "Zona roja: países con menos del 50% de acceso a electricidad. "
        "Eje Y: % de electricidad generada con combustibles fósiles. "
        "Los puntos coloreados son los países en situación crítica."
    )
    st.plotly_chart(_p4_scatter(df_main, params["year_sel"]), use_container_width=True)
    st.divider()

    st.subheader("P5 — Consumo energético per cápita: 2000 vs 2019")
    st.caption("Top 12 países por consumo en 2019. Barra gris = 2000, barra azul = 2019. La diferencia de longitud muestra quién aumentó o redujo su consumo.")
    st.plotly_chart(_p5(df_main), use_container_width=True)
    st.divider()

    # ── P6 ────────────────────────────────────────────────────────────────────
    st.subheader(f"P6 · Mix eléctrico — {params['pais_sel']}")
    st.caption(
        "Barras apiladas por fuente de generación. "
        "La línea roja marca el año de mayor producción renovable."
    )
    st.plotly_chart(_p6_mix(df_main, params["pais_sel"]), use_container_width=True)
    st.divider()

    # ── P7 ────────────────────────────────────────────────────────────────────
    st.subheader("P7 · América Latina: cambio en intensidad de carbono (2000 → 2019)")
    st.caption(
        "Azul: países que redujeron su intensidad de carbono (mejora). "
        "Rojo: países que la aumentaron (empeora). Perú con borde negro."
    )
    st.plotly_chart(_p7_divergente(df_main), use_container_width=True)
    st.divider()