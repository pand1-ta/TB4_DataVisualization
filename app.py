from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "merged-energy-data.csv"

st.set_page_config(page_title="TB4 | Data Visualization", layout="wide", initial_sidebar_state="expanded")

PALETTE = {
	"good": "#1B9E77",
	"bad": "#D95F02",
	"neutral": "#7570B3",
	"accent": "#E7298A",
	"dark": "#1F2937",
	"light": "#F3F4F6",
}


@st.cache_data
def load_data() -> pd.DataFrame:
	df = pd.read_csv(DATA_PATH, low_memory=False)
	df.columns = [column.strip() for column in df.columns]
	df.loc[:, "year"] = pd.to_numeric(df["year"], errors="coerce")
	for column in df.columns:
		if column == "country" or column == "year":
			continue
		converted = pd.to_numeric(df[column], errors="coerce")
		if converted.notna().any():
			df.loc[:, column] = converted
	return df


def find_column(df: pd.DataFrame, candidates: list[str]) -> str:
	for candidate in candidates:
		if candidate in df.columns:
			return candidate
	raise KeyError(f"Missing columns. Tried: {candidates}")


def prepare_region_frame(df: pd.DataFrame) -> pd.DataFrame:
	region_col = "sustainable_region"
	if region_col in df.columns:
		return df
	
	region_map = {
		"Peru": "Latin America",
		"Brazil": "Latin America",
		"Chile": "Latin America",
		"Colombia": "Latin America",
		"Argentina": "Latin America",
		"Mexico": "Latin America",
		"Uruguay": "Latin America",
		"Paraguay": "Latin America",
		"Bolivia": "Latin America",
		"Ecuador": "Latin America",
		"Venezuela": "Latin America",
		"United States": "North America",
		"Canada": "North America",
		"China": "Asia",
		"India": "Asia",
		"Japan": "Asia",
		"Germany": "Europe",
		"France": "Europe",
		"Spain": "Europe",
		"United Kingdom": "Europe",
		"South Africa": "Africa",
		"Nigeria": "Africa",
		"Australia": "Oceania",
	}
	df = df.copy()
	df.loc[:, region_col] = df["country"].map(region_map).fillna("Other")
	return df


def style_figure(fig: go.Figure, height: int = 420) -> go.Figure:
	fig.update_layout(
		height=height,
		margin=dict(l=20, r=20, t=40, b=20),
		paper_bgcolor="white",
		plot_bgcolor="white",
		font=dict(family="Arial, sans-serif", color=PALETTE["dark"]),
	)
	fig.update_xaxes(gridcolor="#E5E7EB", zeroline=False)
	fig.update_yaxes(gridcolor="#E5E7EB", zeroline=False)
	return fig


def color_for_delta(value: float) -> str:
	if value > 0:
		return PALETTE["good"]
	if value < 0:
		return PALETTE["bad"]
	return PALETTE["neutral"]


df = prepare_region_frame(load_data())

owid_renewables = find_column(df, ["owid_renewables_share_energy", "owid_renewables_share_elec"])
owid_gdp = find_column(df, ["sustainable_gdp_per_capita", "owid_gdp"])
owid_access = find_column(df, ["sustainable_access_to_electricity_of_population", "sustainable_access_to_electricity"])
owid_intensity = find_column(df, ["sustainable_energy_intensity_level_of_primary_energy_mj_2017_ppp_gdp", "owid_energy_per_gdp"])
owid_energy_pc = find_column(df, ["owid_energy_per_capita", "sustainable_primary_energy_consumption_per_capita_kwh_person"])
owid_carbon = find_column(df, ["owid_carbon_intensity_elec", "sustainable_value_co2_emissions_kt_by_country"])
owid_fossil = find_column(df, ["owid_fossil_fuel_consumption", "sustainable_electricity_from_fossil_fuels_twh"])
owid_renewables_gen = find_column(df, ["owid_renewables_electricity", "sustainable_electricity_from_renewables_twh"])
owid_coal = find_column(df, ["owid_coal_electricity", "sustainable_electricity_from_fossil_fuels_twh"])
owid_gas = find_column(df, ["owid_gas_electricity", "sustainable_electricity_from_fossil_fuels_twh"])
owid_nuclear = find_column(df, ["owid_nuclear_electricity", "sustainable_electricity_from_nuclear_twh"])
owid_solar = find_column(df, ["owid_solar_electricity", "sustainable_electricity_from_renewables_twh"])
owid_wind = find_column(df, ["owid_wind_electricity", "sustainable_electricity_from_renewables_twh"])
owid_hydro = find_column(df, ["owid_hydro_electricity", "sustainable_electricity_from_renewables_twh"])

countries = sorted([country for country in df["country"].dropna().unique() if isinstance(country, str)])
years = sorted([int(year) for year in df["year"].dropna().unique() if pd.notna(year)])
regions = sorted([region for region in df["sustainable_region"].dropna().unique() if isinstance(region, str)])

st.title("TB4 | Data Visualization")
st.caption("Dashboard preparado para Streamlit Cloud con datos fusionados por country + year.")

with st.sidebar:
	st.header("Controles")
	selected_countries = st.multiselect("Países", countries, default=[country for country in ["Peru", "Chile", "Colombia", "Brazil"] if country in countries])
	selected_regions = st.multiselect("Regiones", regions, default=[region for region in ["Latin America"] if region in regions])
	year_window = st.slider("Rango de años", min_value=min(years), max_value=max(years), value=(2000, 2020))
	selected_year = st.selectbox("Año puntual", [year for year in years if year >= 2000], index=[year for year in years if year >= 2000].index(2020) if 2020 in years else 0)
	peru_country = st.selectbox("País para Perú/vecinos", [country for country in countries if country in ["Peru", "Chile", "Colombia", "Brazil"]], index=0)

start_year, end_year = year_window
filtered_df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

st.subheader("1. Líderes de la transición")
delta_df = df[df["year"].isin([2000, 2020]) & df[owid_renewables].notna()].copy()
delta_pivot = delta_df.pivot_table(index="country", columns="year", values=owid_renewables, aggfunc="mean").dropna()
delta_pivot = delta_pivot.rename(columns={2000: "renewables_2000", 2020: "renewables_2020"})
delta_pivot = delta_pivot.assign(delta=delta_pivot["renewables_2020"] - delta_pivot["renewables_2000"])
top5 = delta_pivot.sort_values("delta", ascending=False).head(5).reset_index()
fig1 = px.bar(top5, x="delta", y="country", orientation="h", color="delta", color_continuous_scale=[PALETTE["bad"], PALETTE["neutral"], PALETTE["good"]], text=top5["delta"].round(2), hover_data={"renewables_2000": ":.2f", "renewables_2020": ":.2f", "delta": ":.2f"})
fig1.update_layout(coloraxis_showscale=False, xaxis_title="Puntos porcentuales ganados", yaxis_title="")
st.plotly_chart(style_figure(fig1), use_container_width=True)

st.subheader("2. Trayectoria regional")
regional = filtered_df[filtered_df["sustainable_region"].isin(selected_regions)].copy()
if regional.empty:
	regional = filtered_df[filtered_df["sustainable_region"].eq("Latin America")].copy()
fig2 = px.line(regional.groupby(["year", "sustainable_region"], as_index=False)[owid_carbon].mean(), x="year", y=owid_carbon, color="sustainable_region", markers=True, color_discrete_sequence=[PALETTE["good"], PALETTE["bad"], PALETTE["neutral"], PALETTE["accent"]])
fig2.update_traces(hovertemplate="Año=%{x}<br>Intensidad=%{y:.2f}<extra></extra>")
st.plotly_chart(style_figure(fig2), use_container_width=True)

st.subheader("3. Riqueza vs. renovables")
scatter_year = df[df["year"] == selected_year].dropna(subset=[owid_gdp, owid_renewables])
fig3 = px.scatter(scatter_year, x=owid_gdp, y=owid_renewables, color="sustainable_region", size="owid_population" if "owid_population" in scatter_year.columns else None, hover_name="country", hover_data={owid_gdp: ":.2f", owid_renewables: ":.2f", "year": True}, color_discrete_sequence=px.colors.qualitative.Safe)
fig3.update_xaxes(title="PIB per cápita")
fig3.update_yaxes(title="Participación de renovables")
st.plotly_chart(style_figure(fig3), use_container_width=True)

st.subheader("4. Pobreza energética y fósiles")
access_year = df[df["year"] == selected_year].dropna(subset=[owid_access, owid_fossil]).copy()
fig4 = px.scatter(access_year, x=owid_access, y=owid_fossil, color=owid_access, color_continuous_scale=[PALETTE["bad"], PALETTE["neutral"], PALETTE["good"]], hover_name="country", hover_data={owid_access: ":.2f", owid_fossil: ":.2f"})
fig4.add_vline(x=50, line_dash="dash", line_color=PALETTE["neutral"])
st.plotly_chart(style_figure(fig4), use_container_width=True)

st.subheader("5. Ranking de consumo")
ranking = df[df["year"].isin([2000, 2020])].groupby(["country", "year"], as_index=False)[owid_energy_pc].mean().dropna()
ranking = ranking.assign(rank=ranking.groupby("year")[owid_energy_pc].rank(method="dense", ascending=False))
ranking = ranking[ranking["rank"] <= 12]
fig5 = px.line(ranking, x="year", y="rank", color="country", markers=True, hover_data={owid_energy_pc: ":.2f", "rank": ":.0f"})
fig5.update_yaxes(autorange="reversed", title="Ranking")
st.plotly_chart(style_figure(fig5), use_container_width=True)

st.subheader("6. Mix eléctrico por país")
mix_country = st.selectbox("País para mix", countries, index=countries.index(peru_country) if peru_country in countries else 0)
mix_country_df = df[df["country"] == mix_country].dropna(subset=[owid_renewables_gen]).copy()
if not mix_country_df.empty:
	peak_year = int(mix_country_df.sort_values(owid_renewables_gen, ascending=False).iloc[0]["year"])
	mix_row = df[(df["country"] == mix_country) & (df["year"] == peak_year)].iloc[0]
	mix_values = {
		"Carbón": float(mix_row.get("owid_coal_electricity", 0) or 0),
		"Gas": float(mix_row.get("owid_gas_electricity", 0) or 0),
		"Nuclear": float(mix_row.get("owid_nuclear_electricity", 0) or 0),
		"Solar": float(mix_row.get("owid_solar_electricity", 0) or 0),
		"Eólica": float(mix_row.get("owid_wind_electricity", 0) or 0),
		"Hidro": float(mix_row.get("owid_hydro_electricity", 0) or 0),
	}
	mix_frame = pd.DataFrame({"Fuente": list(mix_values.keys()), "Generación": list(mix_values.values())})
	fig6 = px.bar(mix_frame, x="Fuente", y="Generación", color="Fuente", color_discrete_sequence=px.colors.qualitative.Safe)
	fig6.update_layout(showlegend=False)
	st.plotly_chart(style_figure(fig6), use_container_width=True)

st.subheader("7. América Latina: mejoraron vs empeoraron")
latin = df[df["sustainable_region"] == "Latin America"].copy()
latin_delta = latin[latin["year"].isin([2000, 2020])].pivot_table(index="country", columns="year", values=owid_carbon, aggfunc="mean").dropna()
latin_delta = latin_delta.assign(delta=latin_delta[2020] - latin_delta[2000])
latin_delta = latin_delta.reset_index().sort_values("delta")
fig7 = px.bar(latin_delta, x="delta", y="country", orientation="h", color="delta", color_continuous_scale=[PALETTE["good"], PALETTE["neutral"], PALETTE["bad"]])
fig7.update_layout(coloraxis_showscale=False)
st.plotly_chart(style_figure(fig7, 520), use_container_width=True)

st.subheader("8. Perú en la región")
peru_region = df[(df["sustainable_region"] == "Latin America") & (df["year"] == selected_year)].copy()
peru_row = peru_region[peru_region["country"].eq("Peru")]
region_means = peru_region[[owid_renewables, owid_access, owid_intensity]].mean(numeric_only=True)
comp_frame = pd.DataFrame(
	{
		"Métrica": ["Renovables", "Acceso", "Intensidad energética"],
		"Perú": [float(peru_row[owid_renewables].mean()) if not peru_row.empty else None, float(peru_row[owid_access].mean()) if not peru_row.empty else None, float(peru_row[owid_intensity].mean()) if not peru_row.empty else None],
		"Promedio LA": [region_means[owid_renewables], region_means[owid_access], region_means[owid_intensity]],
	}
)
fig8 = go.Figure()
fig8.add_bar(x=comp_frame["Métrica"], y=comp_frame["Perú"], name="Perú", marker_color=PALETTE["accent"])
fig8.add_bar(x=comp_frame["Métrica"], y=comp_frame["Promedio LA"], name="Promedio LA", marker_color=PALETTE["neutral"])
fig8.update_layout(barmode="group")
st.plotly_chart(style_figure(fig8), use_container_width=True)

st.subheader("9. Perú vs. vecinos")
neighbors = [country for country in ["Peru", "Chile", "Colombia", "Brazil"] if country in countries]
neighbor_df = df[(df["country"].isin(neighbors)) & (df["year"].between(2000, 2020))].copy()
fig9 = px.line(neighbor_df, x="year", y=owid_energy_pc, color="country", markers=True)
st.plotly_chart(style_figure(fig9), use_container_width=True)

st.subheader("10. Defensa de diseño")
st.info("Usa la visualización que mejor encaja con la pregunta: barras para cambios entre dos momentos, líneas para trayectorias, dispersión para relaciones, y barras apiladas para composición. El encoding principal combina posición, color y tamaño según el objetivo de lectura.")
