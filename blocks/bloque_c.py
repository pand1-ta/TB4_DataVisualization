"""
blocks/bloque_c.py
Bloque C — Posición de Perú
  P8: Perú vs. promedio América Latina en 3 indicadores (barras + línea de referencia)
  P9: Trayectoria energía per cápita — Perú vs Chile, Colombia y Brasil (líneas)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

COLOR_PERU    = "#e63946"
COLOR_LATAM   = "#1a6faf"
COLOR_CHILE   = "#2ecc71"
COLOR_COL     = "#f28e2b"
COLOR_BRAZIL  = "#9b59b6"
COLOR_GREY    = "#d0d0d0"


# ─── P8 ───────────────────────────────────────────────────────────────────────

def _p8(df: pd.DataFrame) -> go.Figure:
    """
    3 paneles apilados verticalmente, uno por indicador.
    Cada panel: barra horizontal de Perú + línea vertical con promedio LA.
    El promedio se muestra como etiqueta sobre la línea, dentro del panel,
    para evitar solapamiento con los títulos de subplots.
    """
    año = 2019
    indicadores = [
        ("Renovables (% energía total)",      "renewable_share_total_energy", "%"),
        ("Acceso a electricidad (%)",          "access_to_electricity",        "%"),
        ("Intensidad energética (MJ/USD PPP)", "energy_intensity_primary",     ""),
    ]

    la   = df[(df["region"] == "América Latina") & (df["year"] == año)]
    peru = df[(df["country"] == "Peru")           & (df["year"] == año)]

    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=[ind[0] for ind in indicadores],
        vertical_spacing=0.22,   # más espacio para que no se solapen títulos y etiquetas
    )

    for i, (label, col, suffix) in enumerate(indicadores, start=1):
        if col not in df.columns:
            continue
        prom_la  = la[col].mean()
        peru_val = peru[col].values[0] if not peru[col].isna().all() else None
        if peru_val is None:
            continue

        # Barra de Perú
        fig.add_trace(go.Bar(
            x=[peru_val], y=["Perú"],
            orientation="h",
            marker_color=COLOR_PERU,
            showlegend=False,
            hovertemplate=f"Perú: {peru_val:.2f}{suffix}<extra></extra>",
            width=0.4,
        ), row=i, col=1)

        # Línea del promedio LA
        fig.add_shape(
            type="line",
            x0=prom_la, x1=prom_la, y0=-0.5, y1=0.5,
            line=dict(color=COLOR_LATAM, width=2.5, dash="dash"),
            row=i, col=1,
        )

        # Etiqueta del promedio anclada al tope del panel
        yref_str = "y domain" if i == 1 else f"y{i} domain"
        xref_str = "x"        if i == 1 else f"x{i}"
        fig.add_annotation(
            x=prom_la,
            y=1.0,
            xref=xref_str,
            yref=yref_str,
            text=f"Prom. LA: {prom_la:.1f}{suffix}",
            showarrow=False,
            yanchor="bottom",
            font=dict(color=COLOR_LATAM, size=10),
            bgcolor="rgba(0,0,0,0)",
        )

        # Etiqueta del valor de Perú a la derecha de la barra
        xref_val = "x" if i == 1 else f"x{i}"
        yref_val = "y" if i == 1 else f"y{i}"
        fig.add_annotation(
            x=peru_val,
            y="Perú",
            xref=xref_val,
            yref=yref_val,
            text=f"  {peru_val:.1f}{suffix}",
            showarrow=False,
            xanchor="left",
            font=dict(color=COLOR_PERU, size=11),
        )

    fig.update_xaxes(showgrid=False, showticklabels=True, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False)
    fig.update_layout(
        title=f"Perú vs. promedio América Latina — {año}",
        height=500,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=40, t=60, b=20),
    )
    return fig


# ─── P9 ───────────────────────────────────────────────────────────────────────

def _p9(df: pd.DataFrame) -> go.Figure:
    """
    4 líneas: Perú en rojo grueso, Chile/Colombia/Brasil en gris fino.
    El foco visual recae enteramente sobre Perú.
    """
    vecinos = ["Peru", "Chile", "Colombia", "Brazil"]

    fig = go.Figure()

    # Primero dibujar los países de comparación (gris, debajo de Perú)
    for pais in vecinos:
        if pais == "Peru":
            continue
        sub = df[df["country"] == pais].dropna(subset=["energy_per_capita"]).sort_values("year")
        if sub.empty:
            continue

        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["energy_per_capita"],
            mode="lines", name=pais,
            line=dict(color=COLOR_GREY, width=1.8),
            hovertemplate=f"<b>{pais}</b><br>Año: %{{x}}<br>%{{y:,.0f}} kWh/persona<extra></extra>",
        ))

        ultimo = sub.iloc[-1]
        fig.add_annotation(
            x=ultimo["year"], y=ultimo["energy_per_capita"],
            text=pais,
            xanchor="left", xshift=6, showarrow=False,
            font=dict(color=COLOR_GREY, size=10),
        )

    # Perú encima, rojo y grueso
    sub_peru = df[df["country"] == "Peru"].dropna(subset=["energy_per_capita"]).sort_values("year")
    fig.add_trace(go.Scatter(
        x=sub_peru["year"], y=sub_peru["energy_per_capita"],
        mode="lines", name="Peru",
        line=dict(color=COLOR_PERU, width=4),
        hovertemplate="<b>Perú</b><br>Año: %{x}<br>%{y:,.0f} kWh/persona<extra></extra>",
    ))
    ultimo_peru = sub_peru.iloc[-1]
    fig.add_annotation(
        x=ultimo_peru["year"], y=ultimo_peru["energy_per_capita"],
        text="<b>Perú</b>",
        xanchor="left", xshift=6, showarrow=False,
        font=dict(color=COLOR_PERU, size=11),
    )

    fig.update_layout(
        title="Consumo de energía per cápita — Perú vs Chile, Colombia y Brasil (2000–2019)",
        xaxis=dict(title="Año", dtick=2, showgrid=False),
        yaxis=dict(title="kWh por persona", showgrid=False),
        height=460,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=100, t=50, b=50),
    )
    return fig


# ─── Render ───────────────────────────────────────────────────────────────────

def render(df_main: pd.DataFrame, params: dict) -> None:
    st.subheader("P8 — Perú vs. promedio América Latina (2019)")
    st.caption("Barra roja = valor de Perú. Línea azul punteada = promedio de América Latina. Tres indicadores, un panel por cada uno.")
    st.plotly_chart(_p8(df_main), use_container_width=True)
    st.divider()

    st.subheader("P9 — Energía per cápita: Perú y vecinos (2000–2019)")
    st.caption("Línea roja y gruesa = Perú. Cuando las líneas convergen, Perú se acerca al grupo; cuando divergen, se aleja.")
    st.plotly_chart(_p9(df_main), use_container_width=True)