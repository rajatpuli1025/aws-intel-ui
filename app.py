import streamlit as st
import requests

st.set_page_config(page_title="AWS Incident Intelligence", layout="wide")

st.title("AWS Incident Intelligence")
st.caption("Predict operational risks from AWS updates (n8n webhook)")

# ---------------- Sidebar Inputs ----------------
st.sidebar.header("Run Analysis")

webhook = st.sidebar.text_input(
    "n8n Webhook URL",
    placeholder="https://<your-public-n8n-url>/webhook/aws-intel"
)

max_items = st.sidebar.number_input("Max items", min_value=1, max_value=50, value=20)

audience = st.sidebar.selectbox(
    "Audience",
    ["cloud_engineer", "developer", "manager"]
)

include_html = st.sidebar.checkbox("Include HTML report", value=True)

scale_mode = st.sidebar.checkbox("Scale mode (10x)", value=False)

run = st.sidebar.button("Run Analysis")

# ---------------- Helper Function ----------------
def call_api(url: str, payload: dict):
    r = requests.post(url, json=payload, timeout=180)
    r.raise_for_status()
    return r.json()

# ---------------- Main Run ----------------
if run:
    if webhook.strip() == "":
        st.error("Please paste your webhook URL")
        st.stop()

    payload = {
        "max_items": int(max_items),
        "audience": audience,
        "include_html": bool(include_html),
        "scale_mode": bool(scale_mode),
    }

    with st.spinner("Calling n8n workflow..."):
        try:
            data = call_api(webhook.strip(), payload)
        except Exception as e:
            st.error(f"API call failed: {e}")
            st.stop()

    st.success("Done!")

    # Show metadata
    st.write("Generated at:", data.get("generated_at", ""))
    st.write("Total items analyzed:", data.get("total_items_analyzed", 0))

    # Items
    items = data.get("items", [])
    if isinstance(items, dict):
        items = [items]

    st.subheader("Items")
    if not items:
        st.warning("No items returned.")
    else:
        for i, it in enumerate(items, start=1):
            st.markdown(f"### {i}. Urgency: {it.get('urgency','')}")
            st.write("Reason:", it.get("reason", ""))
            st.write("Tags:", it.get("tags", []))
            st.write("Impacted services:", it.get("impacted_services", []))
            st.write("Action:", it.get("action_recommendation", ""))
            st.divider()

    # HTML report
    if include_html:
        html_report = data.get("html_report", "") or data.get("html", "")
        if html_report:
            st.subheader("HTML Report")
            st.components.v1.html(html_report, height=800, scrolling=True)
        else:
            st.info("No HTML report returned by API.")
