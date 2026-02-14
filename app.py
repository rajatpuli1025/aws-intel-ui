import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AWS Incident Intelligence", layout="wide")

st.title("AWS Incident Intelligence")
st.caption("Predict operational risks from AWS updates")

# ---------- INPUTS ----------

st.sidebar.header("Run Analysis")

webhook = st.sidebar.text_input(
"n8n Webhook URL",
placeholder="https://xxxx.ngrok-free.app/webhook/aws-intel"
)

max_items = st.sidebar.number_input("Max items", min_value=1, max_value=50, value=20)

audience = st.sidebar.selectbox(
"Audience",
["cloud_engineer", "developer", "manager"]
)

include_html = st.sidebar.checkbox("Include HTML Report", value=True)

run = st.sidebar.button("Run Analysis")

# ---------- RUN ----------

if st.button("Generate Report"):
    resp = call_api(payload)
    st.json(resp)

```
if webhook.strip() == "":
    st.error("Please paste your webhook URL")
    st.stop()

payload = {
    "max_items": max_items,
    "audience": audience,
    "include_html": include_html,
    "scale_mode": False
}

with st.spinner("Analyzing AWS updates..."):
    try:
        r = requests.post(webhook, json=payload, timeout=120)
        data = r.json()
    except Exception as e:
        st.error(f"Request failed: {e}")
        st.stop()

st.success("Analysis Complete")

# ---------- SUMMARY ----------
st.subheader("Summary")
st.write(f"Items analyzed: **{data.get('total_items_analyzed', 0)}**")

# ---------- TABLE ----------
items = data.get("items", [])
if items:
    df = pd.DataFrame(items)
    st.subheader("Findings")
    st.dataframe(df, use_container_width=True)

# ---------- HTML REPORT ----------
html_report = data.get("html_report")
if include_html and html_report:
    st.subheader("Detailed HTML Report")
    st.components.v1.html(html_report, height=800, scrolling=True)
```
