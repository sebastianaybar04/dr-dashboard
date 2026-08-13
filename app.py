"""Streamlit dashboard for Dominican Republic economic indicators (World Bank data)."""
import pandas as pd
import plotly.express as px
import streamlit as st

from fetch_data import INDICATORS, fetch_all

st.set_page_config(page_title="DR Economic Dashboard", page_icon="📊", layout="wide")

LABELS = {
    "gdp_growth": "GDP Growth (annual %)",
    "inflation": "Inflation, Consumer Prices (annual %)",
    "exchange_rate": "Exchange Rate (DOP per USD)",
}


@st.cache_data(ttl=3600)
def load_data() -> dict[str, pd.DataFrame]:
    raw = fetch_all()
    return {
        name: pd.DataFrame(series).rename(columns={"value": name})
        for name, series in raw.items()
    }


st.title("🇩🇴 Dominican Republic Economic Dashboard")
st.caption("Source: World Bank Open Data API")

try:
    data = load_data()
except Exception as e:
    st.error(f"Failed to fetch data from the World Bank API: {e}")
    st.stop()

all_years = sorted(set().union(*[df["year"] for df in data.values()]))
min_year, max_year = min(all_years), max(all_years)

year_range = st.slider(
    "Year range",
    min_value=min_year,
    max_value=max_year,
    value=(max(min_year, max_year - 30), max_year),
)

for name, df in data.items():
    filtered = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    st.subheader(LABELS[name])
    fig = px.line(
        filtered,
        x="year",
        y=name,
        markers=True,
        labels={"year": "Year", name: LABELS[name]},
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    latest = filtered.iloc[-1] if not filtered.empty else None
    if latest is not None:
        st.metric(f"Latest ({int(latest['year'])})", f"{latest[name]:.2f}")

    with st.expander("View raw data"):
        st.dataframe(filtered.sort_values("year", ascending=False), use_container_width=True)
