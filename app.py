import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1VQwpsG2wX1RxCo3Dx5u2foBfxCEf19x4nL_xLk56I5s/export?format=csv"

@st.cache_data(ttl=300)
def load_data():
    return pd.read_csv(SHEET_URL)

df = load_data()

# Detect date column
date_candidates = [c for c in df.columns if c.lower() in ("date", "datetime", "time")]
date_col = date_candidates[0] if date_candidates else df.columns[0]

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df = df.dropna(subset=[date_col]).sort_values(date_col)

numeric_cols = [c for c in df.columns if c != date_col and pd.api.types.is_numeric_dtype(df[c])]

st.title("COT Dashboard")

st.sidebar.header("Show / Hide Series")

selected = []
for col in numeric_cols:
    if st.sidebar.checkbox(col, value=True):
        selected.append(col)

if not selected:
    st.warning("Select at least one series.")
    st.stop()

fig = go.Figure()

for col in selected:
    fig.add_scatter(x=df[date_col], y=df[col], mode="lines", name=col)

fig.update_layout(
    hovermode="x unified",
    xaxis_title=date_col,
    yaxis_title="Value"
)

st.plotly_chart(fig, use_container_width=True)