import streamlit as st
import requests

st.set_page_config(page_title="AWS Incident Intelligence", layout="wide")

st.title("AWS Incident Intelligence")
st.caption("Predict operational risks from AWS updates")

# ---- BACKEND WEBHOOK (YOUR PUBLIC URL) ----
webhook = "https://switched-firewire-monday-filme.trycloudflare.com/webhook/aws-intel"

st.sidebar.header("Run Analysis")

max_items = st.sidebar.number_input("Max items", 1, 50, 20)

audience = st.sidebar.selectbox(
    "Audience",
    ["cloud_engineer", "developer", "manager"]
)

include_html = st.sidebar.checkbox("Include HTML report", value=True)

run = st.sidebar.button("Run Analysis")

# ---- RUN ----
if run:

    payload = {
        "max_items": max_items,
        "audience": audience,
        "include_html": include_html,
        "scale_mode": False
    }

    try:
        with st.spinner("Analyzing AWS updates..."):
            response = requests.post(webhook, json=payload, timeout=300)

        if response.status_code != 200:
            st.error(f"Backend error: {response.status_code}")
            st.text(response.text)
        else:
            data = response.json()
            st.success("Analysis complete!")
            st.json(data)

    except Exception as e:
        st.error("Could not reach backend")
        st.exception(e)
