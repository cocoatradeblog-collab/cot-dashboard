import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="COT Dashboard")

UK_URL = "https://docs.google.com/spreadsheets/d/1VQwpsG2wX1RxCo3Dx5u2foBfxCEf19x4nL_xLk56I5s/export?format=csv"
US_URL = "https://docs.google.com/spreadsheets/d/1B6Mb6rtxGn2CIPrC-lDDjqYAMedrOT-JrHbDsVKiVAI/export?format=csv"

@st.cache_data(ttl=300)
def load_data(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

def prepare_df(df: pd.DataFrame):
    date_candidates = [c for c in df.columns if c.lower() in ("date", "datetime", "time")]
    date_col = date_candidates[0] if date_candidates else df.columns[0]

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).sort_values(date_col)

    numeric_cols = [c for c in df.columns if c != date_col and pd.api.types.is_numeric_dtype(df[c])]
    return df, date_col, numeric_cols

def build_selection(numeric_cols: list[str], key_prefix: str, title: str):
    st.sidebar.markdown(f"## {title}")
    selected = []
    for col in numeric_cols:
        if st.sidebar.checkbox(col, value=True, key=f"{key_prefix}:{col}"):
            selected.append(col)
    return selected

def plot_selected(df: pd.DataFrame, date_col: str, selected: list[str], title: str):
    st.subheader(title)

    if not selected:
        st.warning(f"No series selected for {title}. Select at least one series in the sidebar.")
        return

    fig = go.Figure()
    for col in selected:
        fig.add_scatter(x=df[date_col], y=df[col], mode="lines", name=col)

    fig.update_layout(
        hovermode="x unified",
        xaxis_title=date_col,
        yaxis_title="Value",
        legend_title="Series",
    )
    st.plotly_chart(fig, use_container_width=True)

st.title("COT Dashboard")

# Load both datasets
uk_df, uk_date, uk_cols = prepare_df(load_data(UK_URL))
us_df, us_date, us_cols = prepare_df(load_data(US_URL))

# Sidebar controls (separate groups)
st.sidebar.header("Show / Hide Series")
uk_selected = build_selection(uk_cols, key_prefix="UK", title="UK COT Cocoa")
st.sidebar.divider()
us_selected = build_selection(us_cols, key_prefix="US", title="US COT Cocoa")

# Main page charts (stacked)
plot_selected(uk_df, uk_date, uk_selected, "UK COT Cocoa")
st.divider()
plot_selected(us_df, us_date, us_selected, "US COT Cocoa")
