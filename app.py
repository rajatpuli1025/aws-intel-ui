import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AWS Incident Intelligence", layout="wide")

st.title("AWS Incident Intelligence")
st.caption("Predict operational risks from AWS updates (n8n webhook)")

st.sidebar.header("Run Analysis")

webhook = st.sidebar.text_input(
    "n8n Webhook URL",
    placeholder="https://<your-public-domain>/webhook/aws-intel"
)

max_items = st.sidebar.number_input("Max items", min_value=1, max_value=200, value=20)

audience = st.sidebar.selectbox(
    "Audience",
    ["cloud_engineer", "developer", "manager"]
)

include_html = st.sidebar.checkbox("Include HTML report", value=True)
scale_mode = st.sidebar.checkbox("Scale mode (10x)", value=False)

run = st.sidebar.button("Run Analysis")


def call_api(url: str, payload: dict) -> dict:
    r = requests.post(url, json=payload, timeout=300)
    r.raise_for_status()
    return r.json()


if run:
    if not webhook.strip():
        st.error("Please paste your public n8n webhook URL.")
        st.stop()

    payload = {
        "max_items": int(max_items),
        "audience": audience,
        "include_html": bool(include_html),
        "scale_mode": bool(scale_mode),
    }

    with st.spinner("Analyzing AWS updates..."):
        try:
            data = call_api(webhook, payload)
        except Exception as e:
            st.error(f"API call failed: {e}")
            st.stop()

    st.success("Done!")

    st.subheader("Summary")
    st.write(f"Generated at: {data.get('generated_at', '-')}")
    st.write(f"Total items analyzed: {data.get('total_items_analyzed', 0)}")

    items = data.get("items", [])
    if isinstance(items, dict):
        items = [items]  # safety

    st.subheader("Results")
    if not items:
        st.info("No items returned.")
    else:
        df = pd.DataFrame(items)
        st.dataframe(df, use_container_width=True)

    html_report = data.get("html_report") or data.get("html") or ""
    if include_html and isinstance(html_report, str) and "<html" in html_report.lower():
        st.subheader("HTML Report")
        st.components.v1.html(html_report, height=900, scrolling=True)
