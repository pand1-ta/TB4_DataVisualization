from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="TB4 — Data Visualization",
    page_icon="⚡",
    layout="wide",
)

# Paleta ColorBrewer / colorblind-safe
COLOR_HIGHLIGHT = "#2166ac"      # azul
COLOR_SECONDARY = "#d6604d"      # rojo/anaranjado
COLOR_GREEN = "#1b9e77"          # verde
COLOR_ORANGE = "#d95f02"         # naranja
COLOR_PURPLE = "#7570b3"         # morado
COLOR_GRAY = "#bdbdbd"           # gris para países no destacados
COLOR_DARK_GRAY = "#6c757d"
COLOR_PERU = "#e63946"

QUAL_COLORS = [
    "#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3",
    "#a6d854", "#ffd92f", "#e5c494", "#b3b3b3",
]

DIVERGENT_COLORS = {
    "Mejoró": "#2166ac",
    "Empeoró": "#d6604d",
    "Sin cambio": "#bdbdbd",
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def find_data_file() -> Path:
    """Busca el CSV unido con nombres frecuentes del proyecto."""
    candidates = [
        Path("data/merged.csv"),
        Path("data/energy_merged.csv"),
        Path("data/merged-energy-data.csv"),
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "No se encontró el dataset unido. Verifica que exista data/merged.csv "
        "o ejecuta py data/merge.py."
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    path = find_data_file()
    df = pd.read_csv(path, low_memory=False)
    df.columns = df.columns.str.strip()

    numeric_cols = [
        "year", "population", "gdp", "energy_per_capita",
        "primary_energy_consumption", "fossil_fuel_consumption",
        "fossil_share_energy", "coal_electricity", "gas_electricity",
        "nuclear_electricity", "solar_electricity", "wind_electricity",
        "hydro_electricity", "oil_electricity", "biofuel_electricity",
        "other_renewable_electricity", "coal_share_elec", "gas_share_elec",
        "nuclear_share_elec", "solar_share_elec", "wind_share_elec",
        "hydro_share_elec", "carbon_intensity_elec",
        "renewables_share_energy", "renewables_electricity",
        "access_to_electricity", "access_clean_fuels",
        "renew_elec_cap_per_capita", "financial_flows_usd",
        "renewable_share_total_energy", "elec_from_fossil_twh",
        "elec_from_nuclear_twh", "elec_from_renewables_twh",
        "low_carbon_elec_pct", "primary_energy_per_capita_kwh",
        "energy_intensity_primary", "co2_emissions_kt", "gdp_growth",
        "gdp_per_capita", "population_density", "land_area_km2",
        "latitude", "longitude",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "region" not in df.columns:
        df["region"] = "Otras regiones"
    df["region"] = df["region"].fillna("Otras regiones")

    # Variable unificada para participación renovable.
    # Para comparar 2000–2020 se prioriza OWID porque tiene mayor cobertura en 2020.
    if "renewables_share_energy" in df.columns:
        df["renewable_share_chart"] = df["renewables_share_energy"]
        if "renewable_share_total_energy" in df.columns:
            df["renewable_share_chart"] = df["renewable_share_chart"].combine_first(
                df["renewable_share_total_energy"]
            )
    elif "renewable_share_total_energy" in df.columns:
        df["renewable_share_chart"] = df["renewable_share_total_energy"]
    else:
        df["renewable_share_chart"] = pd.NA

    return df


def filter_year_range(df: pd.DataFrame, start: int = 2000, end: int = 2020) -> pd.DataFrame:
    return df[(df["year"] >= start) & (df["year"] <= end)].copy()


def empty_warning(cols: list[str]) -> None:
    st.warning(
        "No hay datos suficientes para esta visualización con los filtros actuales. "
        f"Columnas esperadas: {', '.join(cols)}"
    )


def add_reference_lines(fig, x: float | None = None, y: float | None = None) -> None:
    if x is not None:
        fig.add_vline(x=x, line_dash="dash", line_color=COLOR_DARK_GRAY)
    if y is not None:
        fig.add_hline(y=y, line_dash="dash", line_color=COLOR_DARK_GRAY)


def safe_metric_pair(df: pd.DataFrame, metric: str, selected_year: int) -> dict | None:
    """Devuelve valor Perú vs promedio LA para el año elegido o el último año disponible."""
    if metric not in df.columns:
        return None

    la = df[df["region"] == "América Latina"].copy()
    peru = df[df["country"] == "Peru"].copy()

    peru_candidates = peru[
        (peru["year"] <= selected_year) & peru[metric].notna()
    ].sort_values("year")

    if peru_candidates.empty:
        return None

    year_used = int(peru_candidates.iloc[-1]["year"])
    peru_value = float(peru_candidates.iloc[-1][metric])

    la_same_year = la[(la["year"] == year_used) & la[metric].notna()]
    if la_same_year.empty:
        return None

    la_avg = float(la_same_year[metric].mean())
    if pd.isna(la_avg) or la_avg == 0:
        return None

    return {
        "year": year_used,
        "peru_value": peru_value,
        "la_avg": la_avg,
        "index_peru": peru_value / la_avg * 100,
        "index_la": 100,
    }


def add_gray_and_highlight_bars(
    df_plot: pd.DataFrame,
    x_col: str,
    y_col: str,
    highlight_col: str,
    title: str,
    x_label: str,
    y_label: str,
    hover_cols: dict,
    height: int = 560,
):
    """Barra horizontal: respuestas destacadas y resto en gris."""
    fig = px.bar(
        df_plot,
        x=x_col,
        y=y_col,
        orientation="h",
        color=highlight_col,
        color_discrete_map={
            "Destacado": COLOR_HIGHLIGHT,
            "Mejoró": COLOR_HIGHLIGHT,
            "Empeoró": COLOR_SECONDARY,
            "Sin cambio": COLOR_GRAY,
            "Otros": COLOR_GRAY,
        },
        text=x_col,
        title=title,
        labels={x_col: x_label, y_col: y_label, highlight_col: "Categoría"},
        hover_data=hover_cols,
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(height=height, yaxis={"categoryorder": "total ascending"})
    return fig


# ============================================================
# CARGA
# ============================================================

try:
    df = load_data()
except Exception as exc:
    st.error(f"Error al cargar los datos: {exc}")
    st.stop()

df_tb4 = filter_year_range(df, 2000, 2020)

required_base = ["country", "year", "region"]
missing_base = [col for col in required_base if col not in df_tb4.columns]
if missing_base:
    st.error(f"Faltan columnas base en el dataset: {missing_base}")
    st.stop()


# ============================================================
# HEADER Y CONTROLES
# ============================================================

st.title("TB4 — Data Visualization")
st.caption("Dashboard interactivo para responder las preguntas de evaluación sobre energía y transición energética.")

with st.sidebar:
    st.header("Controles generales")

    years_available = sorted(df_tb4["year"].dropna().astype(int).unique().tolist())
    min_year = min(years_available) if years_available else 2000
    max_year = max(years_available) if years_available else 2020

    selected_year = st.slider(
        "Año para gráficos comparativos",
        min_value=min_year,
        max_value=max_year,
        value=min(2020, max_year),
        step=1,
    )

    regions_available = sorted(df_tb4["region"].dropna().unique().tolist())
    selected_regions = st.multiselect(
        "Regiones visibles",
        options=regions_available,
        default=regions_available,
    )
    if not selected_regions:
        selected_regions = regions_available

    countries_available = sorted(df_tb4["country"].dropna().unique().tolist())
    default_country = "Peru" if "Peru" in countries_available else countries_available[0]
    selected_country = st.selectbox(
        "País destacado / mix eléctrico",
        options=countries_available,
        index=countries_available.index(default_country),
    )

st.info(
    "Regla visual usada: cuando un gráfico busca identificar países específicos, "
    "los países que responden directamente la pregunta se resaltan en color y el resto queda en gris."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Registros TB4", f"{len(df_tb4):,}")
c2.metric("Países", f"{df_tb4['country'].nunique():,}")
c3.metric("Años", f"{min_year}–{max_year}")
c4.metric("Regiones", f"{df_tb4['region'].nunique():,}")

st.divider()

tabs = st.tabs([
    "P1 Líderes",
    "P2 Regiones",
    "P3 PIB vs renovables",
    "P4 Pobreza energética",
    "P5 Ranking",
    "P6 Mix eléctrico",
    "P7 América Latina",
    "P8 Perú región",
    "P9 Perú vecinos",
    "P10 Defensa",
])


# ============================================================
# P1 — LÍDERES DE LA TRANSICIÓN
# ============================================================

with tabs[0]:
    st.header("Pregunta 1 — Líderes de la transición renovable")
    st.write("Países que más aumentaron su participación renovable entre 2000 y 2020.")

    p1 = df_tb4[
        (df_tb4["year"].isin([2000, 2020])) &
        (df_tb4["renewable_share_chart"].notna())
    ].copy()

    p1_pivot = p1.pivot_table(
        index="country",
        columns="year",
        values="renewable_share_chart",
        aggfunc="mean",
    ).dropna()

    if p1_pivot.empty or 2000 not in p1_pivot.columns or 2020 not in p1_pivot.columns:
        empty_warning(["country", "year", "renewable_share_chart"])
    else:
        p1_pivot["delta_pp"] = p1_pivot[2020] - p1_pivot[2000]

        p1_plot = (
            p1_pivot
            .sort_values("delta_pp", ascending=False)
            .head(15)
            .reset_index()
            .rename(columns={2000: "valor_2000", 2020: "valor_2020"})
        )
        top5_countries = p1_plot.head(5)["country"].tolist()
        p1_plot["categoria"] = p1_plot["country"].apply(
            lambda x: "Destacado" if x in top5_countries else "Otros"
        )

        col_a, col_b = st.columns([2, 1])
        col_a.success("Top 5: " + ", ".join(top5_countries))
        col_b.metric("Mayor aumento", top5_countries[0], f"{p1_plot.iloc[0]['delta_pp']:.2f} pp")

        fig = px.bar(
            p1_plot,
            x="delta_pp",
            y="country",
            orientation="h",
            color="categoria",
            color_discrete_map={"Destacado": COLOR_HIGHLIGHT, "Otros": COLOR_GRAY},
            text="delta_pp",
            title="Aumento de participación renovable: top 5 resaltado, otros países en gris",
            labels={
                "delta_pp": "Aumento 2020 − 2000 (puntos porcentuales)",
                "country": "País",
                "categoria": "Categoría",
                "valor_2000": "Valor 2000",
                "valor_2020": "Valor 2020",
            },
            hover_data={
                "valor_2000": ":.2f",
                "valor_2020": ":.2f",
                "delta_pp": ":.2f",
            },
        )
        fig.update_traces(texttemplate="%{text:.2f} pp", textposition="outside")
        fig.update_layout(height=620, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            p1_plot[["country", "valor_2000", "valor_2020", "delta_pp", "categoria"]],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# P2 — TRAYECTORIA REGIONAL
# ============================================================

with tabs[1]:
    st.header("Pregunta 2 — Trayectoria regional de intensidad de carbono")
    st.write("Evolución de la intensidad de carbono eléctrica por región entre 2000 y 2020.")

    p2 = df_tb4[df_tb4["region"].isin(selected_regions)].copy()
    p2 = p2[p2["carbon_intensity_elec"].notna()]

    if p2.empty:
        empty_warning(["region", "year", "carbon_intensity_elec"])
    else:
        regional = p2.groupby(["year", "region"], as_index=False).agg(
            carbon_intensity_avg=("carbon_intensity_elec", "mean"),
            countries=("country", "nunique"),
            renewable_avg=("renewable_share_chart", "mean"),
        )

        delta_reg = regional[regional["year"].isin([2000, 2020])].pivot_table(
            index="region",
            columns="year",
            values="carbon_intensity_avg",
            aggfunc="mean",
        ).dropna()

        best_region = None
        worst_region = None
        if not delta_reg.empty and 2000 in delta_reg.columns and 2020 in delta_reg.columns:
            delta_reg["delta"] = delta_reg[2020] - delta_reg[2000]
            best_region = delta_reg["delta"].idxmin()
            worst_region = delta_reg["delta"].idxmax()
            col_a, col_b = st.columns(2)
            col_a.metric("Mayor reducción", best_region, f"{delta_reg.loc[best_region, 'delta']:.2f} gCO₂/kWh")
            col_b.metric("Mayor empeoramiento", worst_region, f"{delta_reg.loc[worst_region, 'delta']:.2f} gCO₂/kWh")

        fig = go.Figure()
        for region, region_df in regional.groupby("region"):
            is_best = region == best_region
            is_worst = region == worst_region
            line_color = COLOR_HIGHLIGHT if is_best else COLOR_SECONDARY if is_worst else COLOR_GRAY
            line_width = 4 if (is_best or is_worst) else 1.5
            opacity = 1.0 if (is_best or is_worst) else 0.45

            fig.add_trace(
                go.Scatter(
                    x=region_df["year"],
                    y=region_df["carbon_intensity_avg"],
                    mode="lines+markers",
                    name=region,
                    line=dict(color=line_color, width=line_width),
                    marker=dict(size=7 if (is_best or is_worst) else 4),
                    opacity=opacity,
                    customdata=region_df[["countries", "renewable_avg"]],
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Año: %{x}<br>"
                        "Intensidad carbono: %{y:.2f} gCO₂/kWh<br>"
                        "Países: %{customdata[0]}<br>"
                        "Promedio renovables: %{customdata[1]:.2f}%<extra></extra>"
                    ),
                )
            )

        fig.update_layout(
            title="Trayectoria regional: mejor y peor desempeño resaltados",
            xaxis_title="Año",
            yaxis_title="Intensidad de carbono eléctrica promedio (gCO₂/kWh)",
            height=590,
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# P3 — RIQUEZA VS RENOVABLES
# ============================================================

with tabs[2]:
    st.header("Pregunta 3 — PIB per cápita vs participación de renovables")
    st.write("Relación entre riqueza y participación renovable para el año elegido.")

    p3 = df_tb4[
        (df_tb4["year"] == selected_year) &
        (df_tb4["region"].isin(selected_regions))
    ].copy()
    p3 = p3[p3["gdp_per_capita"].notna() & p3["renewable_share_chart"].notna()]

    if p3.empty:
        empty_warning(["gdp_per_capita", "renewable_share_chart", "year"])
    else:
        top_rich = p3.sort_values("gdp_per_capita", ascending=False).head(8)["country"].tolist()
        p3["categoria"] = "Otros países"
        p3.loc[p3["country"].isin(top_rich), "categoria"] = "Top PIB per cápita"
        p3.loc[p3["country"] == selected_country, "categoria"] = "País seleccionado"

        size_col = "population" if "population" in p3.columns else None

        fig = px.scatter(
            p3,
            x="gdp_per_capita",
            y="renewable_share_chart",
            color="categoria",
            size=size_col,
            size_max=46,
            color_discrete_map={
                "País seleccionado": COLOR_PERU,
                "Top PIB per cápita": COLOR_HIGHLIGHT,
                "Otros países": COLOR_GRAY,
            },
            title=f"PIB per cápita vs renovables — {selected_year}",
            labels={
                "gdp_per_capita": "PIB per cápita",
                "renewable_share_chart": "Participación renovable (%)",
                "population": "Población",
                "categoria": "Categoría",
            },
            hover_name="country",
            hover_data={
                "region": True,
                "access_to_electricity": ":.2f",
                "energy_per_capita": ":.2f",
                "carbon_intensity_elec": ":.2f",
            },
        )
        fig.update_xaxes(type="log")
        fig.update_layout(height=590)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Lectura esperada: los países más ricos no son necesariamente los más renovables. "
            "Los países de mayor PIB se resaltan y el resto queda en gris para evitar ruido visual."
        )


# ============================================================
# P4 — POBREZA ENERGÉTICA Y FÓSILES
# ============================================================

with tabs[3]:
    st.header("Pregunta 4 — Pobreza energética y dependencia fósil")
    st.write("Países con menos de 50% de acceso a electricidad y alta dependencia fósil.")

    p4 = df_tb4[
        (df_tb4["year"] == selected_year) &
        (df_tb4["region"].isin(selected_regions))
    ].copy()
    p4 = p4[p4["access_to_electricity"].notna() & p4["fossil_share_energy"].notna()]

    if p4.empty:
        empty_warning(["access_to_electricity", "fossil_share_energy", "year"])
    else:
        high_fossil_threshold = p4["fossil_share_energy"].quantile(0.75)
        p4["categoria"] = "Otros países"
        p4.loc[
            (p4["access_to_electricity"] < 50) &
            (p4["fossil_share_energy"] >= high_fossil_threshold),
            "categoria"
        ] = "<50% acceso + alta dependencia fósil"

        destacados = p4[p4["categoria"] == "<50% acceso + alta dependencia fósil"].sort_values(
            ["access_to_electricity", "fossil_share_energy"],
            ascending=[True, False],
        )

        col_a, col_b = st.columns(2)
        col_a.metric("Umbral alta dependencia fósil", f"≥ {high_fossil_threshold:.1f}%")
        col_b.metric("Países detectados", len(destacados))

        size_col = "energy_per_capita" if "energy_per_capita" in p4.columns else None

        fig = px.scatter(
            p4,
            x="access_to_electricity",
            y="fossil_share_energy",
            color="categoria",
            size=size_col,
            size_max=40,
            color_discrete_map={
                "<50% acceso + alta dependencia fósil": COLOR_SECONDARY,
                "Otros países": COLOR_GRAY,
            },
            title=f"Acceso a electricidad vs dependencia fósil — {selected_year}",
            labels={
                "access_to_electricity": "Acceso a electricidad (% población)",
                "fossil_share_energy": "Dependencia fósil (% energía)",
                "energy_per_capita": "Energía per cápita",
                "categoria": "Categoría",
            },
            hover_name="country",
            hover_data={
                "region": True,
                "gdp_per_capita": ":.2f",
                "carbon_intensity_elec": ":.2f",
            },
        )
        add_reference_lines(fig, x=50, y=high_fossil_threshold)
        fig.update_layout(height=590)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            destacados[["country", "region", "access_to_electricity", "fossil_share_energy", "energy_per_capita"]],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# P5 — RANKING DE CONSUMO
# ============================================================

with tabs[4]:
    st.header("Pregunta 5 — Ranking de consumo energético per cápita")
    st.write("Movimiento visual del ranking de los doce mayores consumidores de energía per cápita entre 2000 y 2020.")

    p5 = df_tb4[df_tb4["energy_per_capita"].notna()].copy()

    if p5.empty:
        empty_warning(["energy_per_capita", "country", "year"])
    else:
        p5["rank"] = p5.groupby("year")["energy_per_capita"].rank(ascending=False, method="min")

        top12_2020 = (
            p5[p5["year"] == 2020]
            .sort_values("energy_per_capita", ascending=False)
            .head(12)["country"]
            .tolist()
        )

        bump = p5[p5["country"].isin(top12_2020)].copy()

        fig = go.Figure()
        for idx, country in enumerate(top12_2020):
            cdf = bump[bump["country"] == country].sort_values("year")
            fig.add_trace(
                go.Scatter(
                    x=cdf["year"],
                    y=cdf["rank"],
                    mode="lines+markers+text",
                    name=country,
                    line=dict(color=QUAL_COLORS[idx % len(QUAL_COLORS)], width=3),
                    marker=dict(size=7),
                    text=[country if y == 2020 else "" for y in cdf["year"]],
                    textposition="middle right",
                    customdata=cdf[["energy_per_capita", "region"]],
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Año: %{x}<br>"
                        "Ranking: %{y}<br>"
                        "Energía per cápita: %{customdata[0]:.2f}<br>"
                        "Región: %{customdata[1]}<extra></extra>"
                    ),
                )
            )

        fig.update_yaxes(autorange="reversed", dtick=5, title="Posición en ranking")
        fig.update_xaxes(title="Año")
        fig.update_layout(
            title="Bump chart: ranking anual del top 12 de consumo per cápita en 2020",
            height=660,
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

        p5_change = bump[bump["year"].isin([2000, 2020])].pivot_table(
            index="country",
            columns="year",
            values="rank",
            aggfunc="mean",
        ).dropna()

        if not p5_change.empty and 2000 in p5_change.columns and 2020 in p5_change.columns:
            p5_change["cambio_posicion"] = p5_change[2000] - p5_change[2020]
            p5_change = p5_change.reset_index().rename(columns={
                2000: "rank_2000",
                2020: "rank_2020",
            })
            st.caption("Cambio positivo = subió posiciones; cambio negativo = bajó posiciones.")
            st.dataframe(
                p5_change.sort_values("cambio_posicion", ascending=False),
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# P6 — MIX ELÉCTRICO POR PAÍS
# ============================================================

with tabs[5]:
    st.header("Pregunta 6 — Mix eléctrico por país")
    st.write("Para el país seleccionado, se identifica el año de mayor producción renovable y se muestra el mix por fuente.")

    country_df = df_tb4[df_tb4["country"] == selected_country].copy()
    if "renewables_electricity" in country_df.columns:
        country_df = country_df[country_df["renewables_electricity"].notna()]

    if country_df.empty:
        empty_warning(["country", "renewables_electricity"])
    else:
        max_row = country_df.loc[country_df["renewables_electricity"].idxmax()]
        max_year = int(max_row["year"])
        st.metric(
            "Año de mayor producción renovable",
            max_year,
            f"{max_row['renewables_electricity']:.2f} TWh renovables",
        )

        sources = {
            "Carbón": "coal_electricity",
            "Gas": "gas_electricity",
            "Nuclear": "nuclear_electricity",
            "Solar": "solar_electricity",
            "Eólica": "wind_electricity",
            "Hidro": "hydro_electricity",
        }

        mix_rows = []
        for name, col in sources.items():
            value = float(max_row[col]) if col in max_row.index and pd.notna(max_row[col]) else 0.0
            mix_rows.append({"fuente": name, "twh": value})

        mix_df = pd.DataFrame(mix_rows)
        total = mix_df["twh"].sum()
        mix_df["porcentaje"] = mix_df["twh"] / total * 100 if total > 0 else 0
        mix_df["barra"] = "Generación eléctrica"

        fig = px.bar(
            mix_df,
            x="twh",
            y="barra",
            color="fuente",
            orientation="h",
            color_discrete_sequence=QUAL_COLORS,
            title=f"Mix eléctrico de {selected_country} en {max_year}",
            labels={
                "twh": "Generación eléctrica (TWh)",
                "barra": "",
                "fuente": "Fuente",
                "porcentaje": "Porcentaje",
            },
            hover_data={
                "porcentaje": ":.2f",
                "twh": ":.2f",
            },
        )
        fig.update_layout(barmode="stack", height=380)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            mix_df[["fuente", "twh", "porcentaje"]].sort_values("twh", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# P7 — AMÉRICA LATINA
# ============================================================

with tabs[6]:
    st.header("Pregunta 7 — América Latina: cambio en intensidad de carbono")
    st.write("Países latinoamericanos que mejoraron o empeoraron entre 2000 y 2020.")

    p7 = df_tb4[
        (df_tb4["region"] == "América Latina") &
        (df_tb4["year"].isin([2000, 2020])) &
        (df_tb4["carbon_intensity_elec"].notna())
    ].copy()

    p7_pivot = p7.pivot_table(
        index="country",
        columns="year",
        values="carbon_intensity_elec",
        aggfunc="mean",
    ).dropna()

    if p7_pivot.empty or 2000 not in p7_pivot.columns or 2020 not in p7_pivot.columns:
        empty_warning(["country", "region", "year", "carbon_intensity_elec"])
    else:
        p7_pivot["delta"] = p7_pivot[2020] - p7_pivot[2000]
        p7_pivot["estado"] = p7_pivot["delta"].apply(
            lambda x: "Mejoró" if x < 0 else ("Empeoró" if x > 0 else "Sin cambio")
        )

        p7_plot = (
            p7_pivot
            .reset_index()
            .rename(columns={2000: "valor_2000", 2020: "valor_2020"})
            .sort_values("delta")
        )

        improved = int((p7_plot["estado"] == "Mejoró").sum())
        worsened = int((p7_plot["estado"] == "Empeoró").sum())
        col_a, col_b = st.columns(2)
        col_a.metric("Países que mejoraron", improved)
        col_b.metric("Países que empeoraron", worsened)

        fig = px.bar(
            p7_plot,
            x="delta",
            y="country",
            orientation="h",
            color="estado",
            color_discrete_map=DIVERGENT_COLORS,
            text="delta",
            title="Cambio en intensidad de carbono eléctrica en América Latina (2020 − 2000)",
            labels={
                "delta": "Cambio gCO₂/kWh",
                "country": "País",
                "estado": "Resultado",
                "valor_2000": "Valor 2000",
                "valor_2020": "Valor 2020",
            },
            hover_data={
                "valor_2000": ":.2f",
                "valor_2020": ":.2f",
                "delta": ":.2f",
            },
        )
        add_reference_lines(fig, x=0)
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(height=760, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

        st.caption("Valores negativos indican mejora porque la intensidad de carbono disminuyó.")
        st.dataframe(
            p7_plot[["country", "valor_2000", "valor_2020", "delta", "estado"]],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# P8 — PERÚ VS PROMEDIO LATINOAMÉRICA
# ============================================================

with tabs[7]:
    st.header("Pregunta 8 — Perú frente al promedio de América Latina")
    st.write("Comparación multidimensional: renovables, acceso eléctrico e intensidad energética.")

    p8_year = st.slider("Año de referencia para P8", 2000, 2020, 2019, key="p8_year")

    metrics = {
        "Participación renovable": "renewable_share_chart",
        "Acceso a electricidad": "access_to_electricity",
        "Intensidad energética": "energy_intensity_primary",
    }

    rows = []
    for label, metric in metrics.items():
        pair = safe_metric_pair(df_tb4, metric, p8_year)
        if pair:
            rows.append({
                "indicador": label,
                "serie": "Perú",
                "indice_100": pair["index_peru"],
                "valor_real": pair["peru_value"],
                "promedio_la": pair["la_avg"],
                "año_usado": pair["year"],
            })
            rows.append({
                "indicador": label,
                "serie": "Promedio América Latina",
                "indice_100": pair["index_la"],
                "valor_real": pair["la_avg"],
                "promedio_la": pair["la_avg"],
                "año_usado": pair["year"],
            })

    p8_df = pd.DataFrame(rows)

    if p8_df.empty:
        empty_warning(["Peru", "region", "renewable_share_chart", "access_to_electricity", "energy_intensity_primary"])
    else:
        fig = px.bar(
            p8_df,
            x="indicador",
            y="indice_100",
            color="serie",
            barmode="group",
            text="indice_100",
            color_discrete_map={
                "Perú": COLOR_PERU,
                "Promedio América Latina": COLOR_GRAY,
            },
            title="Perú vs promedio latinoamericano — índice 100 = promedio LA",
            labels={
                "indice_100": "Índice comparativo",
                "indicador": "Indicador",
                "serie": "Serie",
            },
            hover_data={
                "valor_real": ":.2f",
                "promedio_la": ":.2f",
                "año_usado": True,
            },
        )
        add_reference_lines(fig, y=100)
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_layout(height=590)
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Lectura: valores sobre 100 indican que Perú está por encima del promedio regional; "
            "valores debajo de 100 indican que está por debajo. El promedio regional queda en gris."
        )
        st.dataframe(p8_df, use_container_width=True, hide_index=True)


# ============================================================
# P9 — PERÚ VS VECINOS
# ============================================================

with tabs[8]:
    st.header("Pregunta 9 — Perú vs Chile, Colombia y Brasil")
    st.write("Trayectoria de consumo de energía per cápita entre 2000 y 2020.")

    neighbors = ["Peru", "Chile", "Colombia", "Brazil"]
    p9 = df_tb4[
        df_tb4["country"].isin(neighbors) &
        df_tb4["energy_per_capita"].notna()
    ].copy()

    if p9.empty:
        empty_warning(["country", "energy_per_capita", "year"])
    else:
        fig = go.Figure()
        for country in neighbors:
            cdf = p9[p9["country"] == country].sort_values("year")
            if cdf.empty:
                continue
            is_peru = country == "Peru"
            fig.add_trace(
                go.Scatter(
                    x=cdf["year"],
                    y=cdf["energy_per_capita"],
                    mode="lines+markers",
                    name=country,
                    line=dict(
                        color=COLOR_PERU if is_peru else COLOR_GRAY,
                        width=4 if is_peru else 2,
                    ),
                    marker=dict(size=8 if is_peru else 5),
                    opacity=1.0 if is_peru else 0.6,
                    customdata=cdf[["carbon_intensity_elec", "renewable_share_chart"]],
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "Año: %{x}<br>"
                        "Energía per cápita: %{y:.2f}<br>"
                        "Intensidad carbono: %{customdata[0]:.2f}<br>"
                        "Participación renovable: %{customdata[1]:.2f}%<extra></extra>"
                    ),
                )
            )

        fig.update_layout(
            title="Consumo de energía per cápita: Perú resaltado frente a vecinos en gris",
            xaxis_title="Año",
            yaxis_title="Energía per cápita",
            height=590,
        )
        st.plotly_chart(fig, use_container_width=True)

        p9_wide = p9.pivot_table(index="year", columns="country", values="energy_per_capita", aggfunc="mean")
        if all(c in p9_wide.columns for c in neighbors):
            p9_wide["promedio_vecinos"] = p9_wide[["Chile", "Colombia", "Brazil"]].mean(axis=1)
            p9_wide["brecha_peru"] = p9_wide["Peru"] - p9_wide["promedio_vecinos"]
            p9_wide["brecha_abs"] = p9_wide["brecha_peru"].abs()

            closest_year = int(p9_wide["brecha_abs"].idxmin())
            farthest_year = int(p9_wide["brecha_abs"].idxmax())

            col1, col2 = st.columns(2)
            col1.metric(
                "Año en que Perú más se acercó al grupo",
                closest_year,
                f"Brecha: {p9_wide.loc[closest_year, 'brecha_peru']:.2f}",
            )
            col2.metric(
                "Año en que Perú más se alejó del grupo",
                farthest_year,
                f"Brecha: {p9_wide.loc[farthest_year, 'brecha_peru']:.2f}",
            )

            st.dataframe(
                p9_wide.reset_index()[["year", "Peru", "promedio_vecinos", "brecha_peru"]],
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# P10 — DEFENSA DE DISEÑO
# ============================================================

with tabs[9]:
    st.header("Pregunta 10 — Defensa de diseño")
    st.write("Guía para responder verbalmente cuando el evaluador seleccione cualquier gráfico.")

    defense = pd.DataFrame([
        ["P1", "Barras horizontales", "País en Y, cambio 2020−2000 en X, color para top 5", "Comparar magnitudes de cambio rápidamente", "Solo muestra los 15 mayores; no todos los países"],
        ["P2", "Líneas múltiples", "Año en X, intensidad promedio en Y, color para mejor/peor región", "Comparar trayectorias temporales", "Promedios regionales pueden ocultar diferencias internas"],
        ["P3", "Scatter plot", "PIB en X, renovables en Y, tamaño población, color para destacados", "Evaluar relación entre dos variables", "Correlación visual no implica causalidad"],
        ["P4", "Scatter plot con umbrales", "Acceso en X, dependencia fósil en Y, tamaño energía per cápita", "Detectar países en zona crítica", "El umbral de alta dependencia depende del percentil elegido"],
        ["P5", "Bump chart", "Año en X, ranking en Y invertido, línea por país", "Rastrear subidas y bajadas de posición", "Con muchas líneas puede haber cruces difíciles de leer"],
        ["P6", "Barra apilada", "Segmentos por fuente eléctrica", "Mostrar composición del mix en un solo año", "No muestra evolución temporal completa"],
        ["P7", "Barras divergentes", "Cambio 2020−2000 en X, país en Y, color dirección", "Distinguir mejora vs empeoramiento", "Depende de tener datos completos para ambos años"],
        ["P8", "Barras agrupadas indexadas", "Indicadores en X, índice relativo en Y, color Perú/promedio", "Comparar tres dimensiones de escalas distintas", "El índice resume y requiere revisar valores reales"],
        ["P9", "Líneas múltiples", "Año en X, energía per cápita en Y, Perú color y vecinos gris", "Comparar trayectoria de Perú con vecinos", "No explica por sí solo las causas de los cambios"],
    ], columns=["Pregunta", "Visualización", "Encoding", "Por qué sirve", "Limitación"])

    st.dataframe(defense, use_container_width=True, hide_index=True)

    st.markdown(
        """
        **Frase base para defender cualquier gráfico:**  
        Elegimos este gráfico porque la pregunta exige comparar una relación específica. 
        El eje X codifica la variable cuantitativa principal, el eje Y organiza países, regiones o años, 
        el color separa categorías o dirección del cambio, y el tooltip agrega métricas de apoyo. 
        La principal limitación es que el gráfico simplifica la realidad y depende de la cobertura disponible de datos.
        """
    )
