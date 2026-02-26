import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="COT Dashboard")

DATASETS = {
    "UK COT Cocoa": "https://docs.google.com/spreadsheets/d/1VQwpsG2wX1RxCo3Dx5u2foBfxCEf19x4nL_xLk56I5s/export?format=csv",
    "US COT Cocoa": "https://docs.google.com/spreadsheets/d/1B6Mb6rtxGn2CIPrC-lDDjqYAMedrOT-JrHbDsVKiVAI/export?format=csv",
}

st.title("COT Dashboard")

dataset_name = st.sidebar.selectbox("Dataset", list(DATASETS.keys()))
sheet_url = DATASETS[dataset_name]

@st.cache_data(ttl=300)
def load_data(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

df = load_data(sheet_url)

# Detect date column
date_candidates = [c for c in df.columns if c.lower() in ("date", "datetime", "time")]
date_col = date_candidates[0] if date_candidates else df.columns[0]

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.dropna(subset=[date_col]).sort_values(date_col)

numeric_cols = [c for c in df.columns if c != date_col and pd.api.types.is_numeric_dtype(df[c])]

st.sidebar.header("Show / Hide Series")

selected = []
for col in numeric_cols:
    if st.sidebar.checkbox(col, value=True, key=f"{dataset_name}:{col}"):
        selected.append(col)

if not selected:
    st.warning("Select at least one series.")
    st.stop()

fig = go.Figure()
for col in selected:
    fig.add_scatter(x=df[date_col], y=df[col], mode="lines", name=col)

fig.update_layout(
    title=f"{dataset_name}",
    hovermode="x unified",
    xaxis_title=date_col,
    yaxis_title="Value",
)

st.plotly_chart(fig, use_container_width=True)
