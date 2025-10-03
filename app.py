import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import random

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="NexaVerse SDP Enterprise Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# COLORS
# =========================
PRIMARY = "#3d5a80"
SECONDARY = "#98c1d9"
HIGHLIGHT = "#ee6c4d"
BG_COLOR = "#e0fbfc"
CARD_BG = "#ffffff"

# =========================
# STYLES
# =========================
st.markdown(f"""
<style>
body {{
    background-color: {BG_COLOR};
    color: {PRIMARY};
    font-family: 'Segoe UI', sans-serif;
}}
h1, h2, h3 {{
    color: {PRIMARY};
}}
.stButton>button {{
    background-color: {PRIMARY};
    color: white;
    border-radius:5px;
}}
.stSidebar {{
    background-color: {PRIMARY};
    color: white;
    font-size:16px;
}}
.stSidebar h2 {{
    color: {SECONDARY};
}}
.card {{
    background-color:{CARD_BG};
    padding:15px;
    border-radius:10px;
    box-shadow: 0px 3px 6px rgba(0,0,0,0.1);
}}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📄 NexaVerse SDP")
menu = {
    "Overview":"overview",
    "Metrics":"metrics",
    "Documents":"documents",
    "Reports":"reports",
    "Settings":"settings"
}

selected = st.sidebar.radio("Navigate", options=list(menu.keys()))

# =========================
# HEADER FUNCTION
# =========================
def display_header(title, subtitle=""):
    st.markdown(f"<h1 style='color:{PRIMARY};'>{title}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<h4 style='color:{SECONDARY};'>{subtitle}</h4>", unsafe_allow_html=True)
    st.markdown("---")

# =========================
# KPI CARD FUNCTION
# =========================
def kpi_card(title, value, delta=None, color=PRIMARY):
    delta_text = f"<p style='color:{HIGHLIGHT}; margin:0'>{delta}</p>" if delta else ""
    st.markdown(f"""
    <div class="card" style="text-align:center; border-left: 5px solid {color}; margin-bottom:10px">
        <h4 style="margin:0">{title}</h4>
        <h2 style="margin:0">{value}</h2>
        {delta_text}
    </div>
    """, unsafe_allow_html=True)

# =========================
# DATA LOADING FUNCTIONS
# =========================
def load_csv_excel():
    st.sidebar.markdown("### Upload CSV or Excel")
    uploaded_file = st.sidebar.file_uploader("Upload file", type=["csv","xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("File loaded successfully ✅")
            return df
        except Exception as e:
            st.error(f"Error loading file: {e}")
    return None

def load_sqlite():
    st.sidebar.markdown("### Connect to SQLite")
    db_file = st.sidebar.text_input("DB File path (SQLite)", "")
    if st.sidebar.button("Load DB"):
        if db_file:
            try:
                conn = sqlite3.connect(db_file)
                df = pd.read_sql("SELECT * FROM documents", conn)
                st.success("DB loaded successfully ✅")
                return df
            except Exception as e:
                st.error(f"Error connecting DB: {e}")
    return None

# =========================
# SIMULATED DATA (fallback)
# =========================
def generate_documents(n=20):
    return pd.DataFrame({
        "DocumentID": range(101,101+n),
        "Type": np.random.choice(["Invoice","Contract","Form","Report"], n),
        "Status": np.random.choice(["Processed","Pending","Error"], n),
        "ProcessedTime": [datetime.now() - timedelta(hours=i*random.randint(1,3)) for i in range(n)]
    })

def generate_trend(days=10):
    dates = [datetime.today() - timedelta(days=i) for i in reversed(range(days))]
    values = np.random.randint(1000,2000, size=days)
    return pd.DataFrame({"Date": dates, "Processed Docs": values})

# =========================
# LOAD DATA
# =========================
data = load_csv_excel() or load_sqlite() or generate_documents(20)

# =========================
# OVERVIEW PAGE
# =========================
if menu[selected]=="overview":
    display_header("Smart Document Processing Dashboard","Enterprise Overview")

    processed_count = len(data[data['Status']=='Processed'])
    pending_count = len(data[data['Status']=='Pending'])
    error_count = len(data[data['Status']=='Error'])
    accuracy = f"{round(processed_count/(processed_count+error_count+1)*100,2)}%"

    # KPI CARDS
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Processed Docs", processed_count)
    col2.metric("Pending Docs", pending_count)
    col3.metric("Accuracy Rate", accuracy)
    col4.metric("Processing Speed", f"{round(np.random.uniform(4,6),1)} docs/sec")

    st.markdown("### 📈 Recent Processing Trends")
    trend_data = generate_trend()
    fig = px.line(trend_data, x="Date", y="Processed Docs", markers=True)
    fig.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig, use_container_width=True)

# =========================
# METRICS PAGE
# =========================
elif menu[selected]=="metrics":
    display_header("Processing Accuracy & Speed Metrics")
    st.subheader("Accuracy by Document Type")
    doc_types = data['Type'].unique()
    accuracy_vals = [round(len(data[(data['Type']==t) & (data['Status']=='Processed')]) / 
                    (len(data[data['Type']==t])+1)*100,2) for t in doc_types]
    fig = px.bar(
        x=doc_types, y=accuracy_vals,
        color=accuracy_vals, color_continuous_scale=[HIGHLIGHT, SECONDARY],
        labels={"x":"Document Type","y":"Accuracy %"}
    )
    fig.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Processing Time Distribution (seconds)")
    if 'ProcessedTime' in data.columns:
        times = np.random.normal(5,1.2,len(data))
        fig2 = px.histogram(x=times, nbins=15, color_discrete_sequence=[HIGHLIGHT])
        fig2.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, use_container_width=True)

# =========================
# DOCUMENTS PAGE
# =========================
elif menu[selected]=="documents":
    display_header("Latest Documents Processed")
    status_filter = st.multiselect("Filter by Status", options=data['Status'].unique(), default=list(data['Status'].unique()))
    filtered_docs = data[data['Status'].isin(status_filter)]
    st.dataframe(filtered_docs)

# =========================
# REPORTS PAGE
# =========================
elif menu[selected]=="reports":
    display_header("Monthly Document Processing Report")
    months = [datetime.today()-timedelta(days=i*30) for i in range(9)][::-1]
    report_df = pd.DataFrame({
        "Month": [d.strftime("%b") for d in months],
        "Processed": np.random.randint(8000,15000,9),
        "Errors": np.random.randint(50,300,9)
    })
    fig = px.line(report_df, x="Month", y=["Processed","Errors"], markers=True)
    fig.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig, use_container_width=True)

# =========================
# SETTINGS PAGE
# =========================
elif menu[selected]=="settings":
    display_header("Dashboard Settings")
    st.write("Customize notifications, user roles, and processing thresholds")
    notify = st.checkbox("Enable notifications", True)
    threshold = st.slider("Error Threshold (%)", 0, 10, 5)
    st.write("Settings saved ✅")
