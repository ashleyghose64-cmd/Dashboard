import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 seconds
count = st_autorefresh(interval=5000, limit=None, key="dashboard_refresh")

st.set_page_config(page_title="NexaVerse SDP Live Dashboard", layout="wide", initial_sidebar_state="expanded")

PRIMARY = "#3d5a80"
SECONDARY = "#98c1d9"
HIGHLIGHT = "#ee6c4d"
BG_COLOR = "#e0fbfc"
CARD_BG = "#ffffff"

st.markdown(f"""
<style>
body {{ background-color: {BG_COLOR}; color: {PRIMARY}; font-family: 'Segoe UI', sans-serif; }}
h1, h2, h3 {{ color: {PRIMARY}; }}
.stButton>button {{ background-color: {PRIMARY}; color: white; border-radius: 5px; }}
.stSidebar {{ background-color: {PRIMARY}; color: white; font-size:16px; }}
.stSidebar h2 {{ color: {SECONDARY}; }}
.card {{ background-color: {CARD_BG}; padding:15px; border-radius:10px; box-shadow: 0px 3px 6px rgba(0,0,0,0.1); }}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("📄 NexaVerse SDP Live")
menu = {"Overview":"overview","Metrics":"metrics","Documents":"documents","Reports":"reports","Settings":"settings"}
selected = st.sidebar.radio("Navigate", options=list(menu.keys()))

def display_header(title, subtitle=""):
    st.markdown(f"<h1 style='color:{PRIMARY};'>{title}</h1>", unsafe_allow_html=True)
    if subtitle: st.markdown(f"<h4 style='color:{SECONDARY};'>{subtitle}</h4>", unsafe_allow_html=True)
    st.markdown("---")

def generate_documents(n=20):
    return pd.DataFrame({
        "DocumentID": range(101,101+n),
        "Type": np.random.choice(["Invoice","Contract","Form","Report"], n),
        "Status": np.random.choice(["Processed","Pending","Error"], n),
        "ProcessedTime": [datetime.now() - timedelta(seconds=i*random.randint(10,300)) for i in range(n)]
    })

def generate_trend(days=10):
    dates = [datetime.today() - timedelta(days=i) for i in reversed(range(days))]
    values = np.random.randint(1000,2000, size=days)
    return pd.DataFrame({"Date": dates, "Processed Docs": values})

# Initialize session state
if 'docs' not in st.session_state:
    st.session_state.docs = generate_documents(30)
if 'trend' not in st.session_state:
    st.session_state.trend = generate_trend(10)

def live_update():
    # Add new document
    new_doc = pd.DataFrame({
        "DocumentID": [st.session_state.docs['DocumentID'].max()+1],
        "Type": [random.choice(["Invoice","Contract","Form","Report"])],
        "Status": [random.choices(["Processed","Pending","Error"], weights=[0.7,0.2,0.1])[0]],
        "ProcessedTime": [datetime.now()]
    })
    st.session_state.docs = pd.concat([st.session_state.docs, new_doc], ignore_index=True)
    
    # Update trend
    new_value = np.random.randint(1000,2000)
    new_row = pd.DataFrame([{"Date": datetime.now(), "Processed Docs": new_value}])
    st.session_state.trend = pd.concat([st.session_state.trend, new_row], ignore_index=True)
    
    # Keep only last 10 trend points
    if len(st.session_state.trend) > 10:
        st.session_state.trend = st.session_state.trend.iloc[1:]

# Pages
if menu[selected]=="overview":
    display_header("Smart Document Processing Dashboard (Live)", "Real-time Monitoring")
    col1, col2, col3, col4 = st.columns(4)
    processed_count = len(st.session_state.docs[st.session_state.docs['Status']=='Processed'])
    pending_count = len(st.session_state.docs[st.session_state.docs['Status']=='Pending'])
    error_count = len(st.session_state.docs[st.session_state.docs['Status']=='Error'])
    accuracy = f"{round(processed_count/(processed_count+error_count+1)*100,2)}%"
    col1.metric("Processed Docs", processed_count)
    col2.metric("Pending Docs", pending_count)
    col3.metric("Accuracy Rate", accuracy)
    col4.metric("Processing Speed", f"{round(np.random.uniform(4,6),1)} docs/sec")
    
    st.markdown("### 📈 Recent Processing Trends")
    fig = px.line(st.session_state.trend, x="Date", y="Processed Docs", markers=True)
    fig.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig, use_container_width=True)

elif menu[selected]=="documents":
    display_header("Latest Documents Processed")
    status_filter = st.multiselect("Filter by Status", options=st.session_state.docs['Status'].unique(), default=list(st.session_state.docs['Status'].unique()))
    filtered_docs = st.session_state.docs[st.session_state.docs['Status'].isin(status_filter)]
    st.dataframe(filtered_docs)

elif menu[selected]=="metrics":
    display_header("Processing Accuracy & Speed Metrics")
    doc_types = st.session_state.docs['Type'].unique()
    accuracy_vals = [round(len(st.session_state.docs[(st.session_state.docs['Type']==t) & (st.session_state.docs['Status']=='Processed')]) / 
                    (len(st.session_state.docs[st.session_state.docs['Type']==t])+1)*100,2) for t in doc_types]
    fig = px.bar(x=doc_types, y=accuracy_vals, color=accuracy_vals, color_continuous_scale=[HIGHLIGHT, SECONDARY],
                 labels={"x":"Document Type","y":"Accuracy %"})
    fig.update_layout(paper_bgcolor=BG_COLOR, plot_bgcolor=BG_COLOR, showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig, use_container_width=True)

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

elif menu[selected]=="settings":
    display_header("Dashboard Settings")
    notify = st.checkbox("Enable notifications", True)
    threshold = st.slider("Error Threshold (%)", 0, 10, 5)
    st.write("Settings saved ✅")

# Update live data every refresh
if menu[selected] in ["overview","documents","metrics"]:
    live_update()
