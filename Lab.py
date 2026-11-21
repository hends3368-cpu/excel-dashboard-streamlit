import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Excel Dashboard", layout="wide")
st.title("📊 Excel Dashboard (Streamlit)")

@st.cache_data(show_spinner=False)
def load_excel(uploaded_file, sheet_name=None):
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all")  # شيل الصفوف الفاضية خالص
    return df

# Sidebar
st.sidebar.header("📁 Excel File")
uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file is None:
    st.info("ارفعي ملف Excel من القائمة الجانبية عشان يظهر الداشبورد.")
    st.stop()

# Get sheet names
try:
    xls = pd.ExcelFile(uploaded_file)
except Exception as e:
    st.error(f"مش قادر أقرأ الملف: {e}")
    st.stop()

sheet_name = st.sidebar.selectbox("Choose Sheet", xls.sheet_names)
df = load_excel(uploaded_file, sheet_name=sheet_name)

if df.empty:
    st.warning("الشيت ده فاضي.")
    st.stop()

# KPIs
cols = df.columns.tolist()
numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]

k1, k2, k3 = st.columns(3)
k1.metric("Rows", f"{len(df):,}")
k2.metric("Columns", len(cols))
k3.metric("Numeric columns", len(numeric_cols))

st.subheader(f"Preview — Sheet: {sheet_name}")
st.dataframe(df, use_container_width=True, height=300)

# Choose chart columns
st.subheader("📈 Chart")

if not numeric_cols:
    st.warning("لا يوجد أعمدة رقمية لرسم Y. حوّلي عمود المبيعات/القيم لأرقام في Excel.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
x_col = c1.selectbox("X column", cols)
y_col = c2.selectbox("Y column (numeric)", numeric_cols)
agg = c3.selectbox("Aggregation", ["Sum", "Average", "Count", "None"])
chart_type = c4.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Pie"])

# تجميع البيانات حسب عمود X
if agg == "None" or x_col == y_col:
    chart_df = df[[x_col, y_col]]
else:
    func = {"Sum": "sum", "Average": "mean", "Count": "count"}[agg]
    chart_df = df.groupby(x_col, as_index=False)[y_col].agg(func)

if chart_type == "Bar":
    fig = px.bar(chart_df, x=x_col, y=y_col)
elif chart_type == "Line":
    fig = px.line(chart_df, x=x_col, y=y_col, markers=True)
elif chart_type == "Pie":
    fig = px.pie(chart_df, names=x_col, values=y_col)
else:
    fig = px.scatter(chart_df, x=x_col, y=y_col)

st.plotly_chart(fig, use_container_width=True)

# Summary
st.subheader("🧮 Summary")
st.dataframe(df[numeric_cols].describe().T, use_container_width=True)

# Download
st.download_button(
    "⬇️ Download chart data (CSV)",
    chart_df.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"{sheet_name}_{y_col}.csv",
    mime="text/csv",
)


## python -m streamlit run Lab.py
