import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="AWS Incident Intelligence", layout="wide")

st.title("AWS Incident Intelligence")
st.caption("Predict operational risks from AWS updates (n8n webhook)")

# ---- SIDEBAR ----
st.sidebar.header("Run Analysis")

# Webhook URL input with your production URL pre-filled
webhook = st.sidebar.text_input(
    "n8n Webhook URL",
    value="https://aws-intel.app.n8n.cloud/webhook/aws-intel",
    placeholder="https://<your-public-domain>/webhook/aws-intel"
)

# Max items slider
max_items = st.sidebar.number_input("Max items", min_value=1, max_value=200, value=20)

# Audience selector
audience = st.sidebar.selectbox(
    "Audience",
    ["cloud_engineer", "developer", "manager"]
)

# Checkboxes
include_html = st.sidebar.checkbox("Include HTML report", value=True)
scale_mode = st.sidebar.checkbox("Scale mode (10x)", value=False)

# Run button
run = st.sidebar.button("Run Analysis")

# ---- HELPER FUNCTION ----
def call_api(url: str, payload: dict) -> dict:
    """Call the n8n webhook with error handling"""
    r = requests.post(url, json=payload, timeout=300)
    r.raise_for_status()
    return r.json()

# ---- MAIN LOGIC ----
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
    
    with st.spinner("Analyzing AWS updates... This may take 1-2 minutes."):
        try:
            data = call_api(webhook, payload)
        except requests.exceptions.Timeout:
            st.error("Request timed out. The workflow might be taking too long. Try reducing max_items.")
            st.stop()
        except requests.exceptions.RequestException as e:
            st.error(f"API call failed: {e}")
            st.stop()
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
    
    st.success("Done!")
    
    # ---- DISPLAY RESULTS ----
    st.subheader("Summary")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Generated at", data.get('generated_at', '--'))
    with col2:
        st.metric("Total items analyzed", data.get('total_items_analyzed', 0))
    
    # Get items
    items = data.get("items", [])
    if isinstance(items, dict):
        items = [items]  # safety
    
    st.subheader("Results")
    if not items:
        st.info("No items returned.")
    else:
        # Create dataframe
        df = pd.DataFrame(items)
        
        # Display with better formatting
        st.dataframe(df, use_container_width=True, height=400)
        
        # Download button for CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download results as CSV",
            data=csv,
            file_name="aws_incident_analysis.csv",
            mime="text/csv"
        )
        
        # HTML Report
        html_report = data.get("html_report") or data.get("html") or ""
        if include_html and isinstance(html_report, str) and "<html" in html_report.lower():
            st.subheader("HTML Report")
            st.components.v1.html(html_report, height=900, scrolling=True)
else:
    # ---- INFO SECTION ----
    st.info("👈 Configure settings in the sidebar and click 'Run Analysis' to get started")
    
    st.markdown("---")
    
    # Two-column layout for better presentation
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 What it does")
        st.markdown("""
        This tool analyzes AWS service updates and predicts operational risks using AI:
        
        - Monitors **AWS What's New**, **Blog posts**, and **Info/Q News**
        - Uses **OpenAI GPT-4** to assess impact and urgency
        - Generates risk scores (P0-P2) for each update
        - Provides actionable recommendations
        - Creates detailed HTML reports
        """)
        
        st.subheader("👥 Who it's for")
        st.markdown("""
        - **Cloud Engineers**: Stay ahead of service changes
        - **DevOps Teams**: Plan infrastructure updates
        - **Engineering Managers**: Assess operational risks
        """)
    
    with col2:
        st.subheader("🛠️ Tech Stack")
        st.markdown("""
        - **n8n**: Workflow automation
        - **OpenAI GPT-4.1-Mini**: AI analysis
        - **Streamlit**: User interface
        - **AWS RSS Feeds**: Data source
        """)
        
        st.subheader("📝 How to use")
        st.markdown("""
        1. Select your **audience type** (determines analysis focus)
        2. Set **max items** to analyze (1-200)
        3. Toggle **HTML report** for detailed view
        4. Enable **scale mode** for 10x processing
        5. Click **Run Analysis** and wait 1-2 minutes
        6. Review results and download CSV if needed
        """)
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>Created by:</strong> Rajat</p>
        <p><strong>Assignment:</strong> A5 - Public API Wrapper</p>
        <p><strong>Course:</strong> Cloud Engineering & Automation</p>
    </div>
    """, unsafe_allow_html=True)
