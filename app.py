import streamlit as st
import requests
import json

st.set_page_config(page_title="AWS Incident Intelligence", layout="wide")

st.title("AWS Incident Intelligence")
st.caption("Predict operational risks from AWS updates")

# ---------------- SIDEBAR ----------------

st.sidebar.header("Run Analysis")

webhook = st.sidebar.text_input(
"n8n Production Webhook URL",
placeholder="https://xxxx.ngrok-free.app/webhook/aws-intel"
)

max_items = st.sidebar.number_input("Max items", min_value=1, max_value=50, value=20)

audience = st.sidebar.selectbox(
"Audience",
["cloud_engineer", "developer", "manager"]
)

include_html = st.sidebar.checkbox("Include HTML Report", value=True)

run = st.sidebar.button("Run Analysis")

# ---------------- FUNCTION ----------------

def call_api(url, payload):
try:
response = requests.post(url, json=payload, timeout=120)
if response.status_code != 200:
st.error(f"Server returned {response.status_code}")
return None
return response.json()
except Exception as e:
st.error(f"Connection failed: {e}")
return None

# ---------------- RUN ----------------

if run:

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
    data = call_api(webhook, payload)

if not data:
    st.stop()

st.success("Analysis complete")

# ---------- SUMMARY ----------
st.subheader("Summary")
st.write(f"Generated at: {data.get('generated_at','-')}")
st.write(f"Items analyzed: {data.get('total_items_analyzed',0)}")

# ---------- ITEMS ----------
st.subheader("Detected Risks")

items = data.get("items", [])

if len(items) == 0:
    st.info("No risks detected")
else:
    for i, item in enumerate(items, 1):
        with st.expander(f"Risk #{i} — {item.get('urgency','Unknown')}"):
            st.write("**Reason:**", item.get("reason",""))
            st.write("**Services:**", ", ".join(item.get("impacted_services",[])))
            st.write("**Tags:**", ", ".join(item.get("tags",[])))
            st.write("**Recommendation:**", item.get("action_recommendation",""))

# ---------- HTML REPORT ----------
html_report = data.get("html_report","")

if include_html and html_report:
    st.subheader("HTML Report")
    st.components.v1.html(html_report, height=800, scrolling=True)
```

