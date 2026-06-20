"""
blocks/bloque_a.py
Bloque A — Panorama global
  P1: Top 15 países con mayor aumento renovable (barras horizontales)
  P2: Trayectoria regional de intensidad de carbono (líneas múltiples)
  P3: PIB per cápita vs. renovables (scatter con tendencia y escala log)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from blocks.data_loader import COLORS_REGION

COLOR_TOP   = "#1a6faf"
COLOR_REST  = "#d0d0d0"
COLOR_BEST  = "#1a6faf"
COLOR_WORST = "#c0392b"
COLOR_GREY  = "#c8c8c8"
COLOR_TREND = "#e67e22"


# ─── P1 ───────────────────────────────────────────────────────────────────────

def _p1(df: pd.DataFrame) -> go.Figure:
    piv = (
        df[df["year"].isin([2000, 2019])]
        .pivot_table(index="country", columns="year", values="renewable_share_total_energy")
        .dropna()
    )
    piv.columns = ["y2000", "y2019"]
    piv["delta"] = piv["y2019"] - piv["y2000"]
    piv = piv.sort_values("delta", ascending=False).head(15).sort_values("delta", ascending=True).reset_index()

    top5  = set(piv.nlargest(5, "delta")["country"])
    colors = [COLOR_TOP if c in top5 else COLOR_REST for c in piv["country"]]

    fig = go.Figure(go.Bar(
        x=piv["delta"],
        y=piv["country"],
        orientation="h",
        marker_color=colors,
        hovertemplate="<b>%{y}</b><br>+%{x:.1f} pp (2000→2019)<extra></extra>",
    ))

    for _, row in piv[piv["country"].isin(top5)].iterrows():
        fig.add_annotation(
            x=row["delta"] + 0.3, y=row["country"],
            text=f"<b>+{row['delta']:.1f} pp</b>",
            xanchor="left", showarrow=False,
            font=dict(color=COLOR_TOP, size=11),
        )

    fig.update_layout(
        title="Top 15 países con mayor aumento en participación renovable (2000 → 2019)",
        xaxis=dict(title="Puntos porcentuales ganados", showgrid=False, zeroline=False),
        yaxis=dict(title="", showgrid=False),
        height=480,
        margin=dict(l=160, r=120, t=50, b=40),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ─── P2 ───────────────────────────────────────────────────────────────────────

def _p2(df: pd.DataFrame, regiones_sel: list) -> go.Figure:
    df_p2 = (
        df[df["region"].isin(regiones_sel)]
        .groupby(["region", "year"])["carbon_intensity_elec"]
        .mean()
        .reset_index()
    )

    deltas = (
        df_p2[df_p2["year"].isin([2000, 2019])]
        .pivot_table(index="region", columns="year", values="carbon_intensity_elec")
        .dropna()
    )
    mejor = peor = None
    if not deltas.empty:
        deltas.columns = ["y2000", "y2019"]
        deltas["delta"] = deltas["y2019"] - deltas["y2000"]
        mejor = deltas["delta"].idxmin()
        peor  = deltas["delta"].idxmax()

    fig = go.Figure()
    for region in sorted(df_p2["region"].unique()):
        sub = df_p2[df_p2["region"] == region].sort_values("year")
        if region == mejor:
            color, width = COLOR_BEST, 3.5
        elif region == peor:
            color, width = COLOR_WORST, 3.5
        else:
            color, width = COLOR_GREY, 1.5

        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["carbon_intensity_elec"],
            mode="lines", name=region,
            line=dict(color=color, width=width),
            hovertemplate=f"<b>{region}</b><br>Año: %{{x}}<br>%{{y:.1f}} gCO₂/kWh<extra></extra>",
        ))

    for region, color, label in [(mejor, COLOR_BEST, "Mayor reducción"), (peor, COLOR_WORST, "Mayor aumento")]:
        if region:
            val = df_p2[(df_p2["region"] == region) & (df_p2["year"] == 2019)]
            if not val.empty:
                fig.add_annotation(
                    x=2019, y=val["carbon_intensity_elec"].values[0],
                    text=f"<b>{region} — {label}</b>",
                    xanchor="left", xshift=8, showarrow=False,
                    font=dict(color=color, size=11),
                )

    fig.update_layout(
        title="Intensidad de carbono eléctrica promedio por región (2000–2019)",
        xaxis=dict(title="Año", dtick=2, showgrid=False),
        yaxis=dict(title="gCO₂/kWh promedio", showgrid=False),
        height=460,
        margin=dict(l=60, r=240, t=50, b=40),
        legend=dict(title="Región", x=1.02, orientation="v"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ─── P3 ───────────────────────────────────────────────────────────────────────

def _p3(df: pd.DataFrame, year_sel: int) -> go.Figure:
    df_p3 = (
        df[df["year"] == year_sel]
        .dropna(subset=["gdp_per_capita", "renewable_share_total_energy"])
        .copy()
    )

    x = df_p3["gdp_per_capita"].values
    y = df_p3["renewable_share_total_energy"].values
    # Regresión en escala log para manejar la dispersión del PIB
    log_x = np.log10(x)
    m, b = np.polyfit(log_x, y, 1)
    x_range = np.linspace(x.min(), x.max(), 300)
    y_trend = m * np.log10(x_range) + b
    corr = np.corrcoef(log_x, y)[0, 1]

    fig = go.Figure()

    # Un solo color neutro para todos los puntos — el mensaje es la tendencia
    fig.add_trace(go.Scatter(
        x=df_p3["gdp_per_capita"],
        y=df_p3["renewable_share_total_energy"],
        mode="markers",
        name="País",
        marker=dict(color=COLOR_GREY, size=7, opacity=0.8,
                    line=dict(color="white", width=0.4)),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "PIB per cápita: %{x:,.0f} USD<br>"
            "Renovables: %{y:.1f}%<extra></extra>"
        ),
        customdata=df_p3[["country"]].values,
        showlegend=False,
    ))

    # Línea de tendencia
    fig.add_trace(go.Scatter(
        x=x_range, y=y_trend,
        mode="lines",
        name=f"Tendencia (r = {corr:.2f})",
        line=dict(color=COLOR_TREND, width=2.5, dash="dash"),
        hoverinfo="skip",
    ))

    # Anotación de correlación
    direccion = "negativa" if corr < 0 else "positiva"
    fig.add_annotation(
        x=0.97, y=0.95, xref="paper", yref="paper",
        text=f"<b>Correlación {direccion}: r = {corr:.2f}</b><br>Los países más ricos no son<br>necesariamente los más renovables.",
        showarrow=False,
        font=dict(size=12, color=COLOR_TREND),
        align="right",
        bgcolor="rgba(0,0,0,0)",
        bordercolor=COLOR_TREND,
        borderwidth=1,
    )

    fig.update_layout(
        title=f"¿Los países más ricos son los más renovables? ({year_sel})",
        xaxis=dict(
            title="PIB per cápita (USD, escala logarítmica)",
            type="log",
            showgrid=False,
        ),
        yaxis=dict(
            title="Participación renovable (% energía total)",
            ticksuffix="%",
            showgrid=False,
        ),
        height=460,
        margin=dict(l=60, r=40, t=50, b=50),
        legend=dict(orientation="h", y=-0.12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ─── Render ───────────────────────────────────────────────────────────────────

def render(df_main: pd.DataFrame, params: dict) -> None:
    st.subheader("P1 — Líderes de la transición renovable (2000 → 2019)")
    st.caption("Top 15 países por aumento en participación de energías renovables. En azul: los 5 con mayor incremento.")
    st.plotly_chart(_p1(df_main), use_container_width=True)
    st.divider()

    st.subheader("P2 — Trayectoria regional de intensidad de carbono (2000–2019)")
    st.caption("Azul: región con mayor reducción. Rojo: región con mayor aumento. Gris: resto.")
    st.plotly_chart(_p2(df_main, params["regiones_sel"]), use_container_width=True)
    st.divider()

    st.subheader(f"P3 — PIB per cápita vs. participación renovable ({params['year_sel']})")
    st.caption("Escala logarítmica en el eje X para distribuir los países de forma legible. La línea punteada muestra la tendencia global.")
    st.plotly_chart(_p3(df_main, params["year_sel"]), use_container_width=True)