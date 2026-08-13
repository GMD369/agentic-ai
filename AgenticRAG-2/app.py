import streamlit as st
import os
import tempfile
import backend

st.set_page_config(page_title="Agentic Project Evaluator", layout="wide")

st.title("🤖 Project Feasibility AI Agent")
st.markdown("Upload a client project file or link to check if our organization can handle it.")

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key Input
    api_key = st.text_input("Groq API Key", type="password")
    if not api_key:
        st.warning("Please enter your Groq API Key to proceed.")
        st.stop()
        
    st.divider()
    
    # Load Company Docs
    st.subheader("📁 Company Knowledge Base")
    st.info("Ensure your brochures/profiles are in the 'company_docs' folder.")
    
    if st.button("🔄 Refresh/Load Company Docs"):
        with st.spinner("Ingesting Company PDFs..."):
            # Call backend to extract text from all company PDFs
            org_docs_text = backend.upload_org_docs("company_docs")
            st.session_state.org_docs_text = org_docs_text

            if org_docs_text:
                st.success("Loaded company documents into AI Memory.")
            else:
                st.error("No PDFs found in 'company_docs' folder!")

    # Show loaded status
    if st.session_state.get("org_docs_text"):
        st.write("✅ Active Context: company docs loaded")
    else:
        st.write("❌ No docs loaded.")

# --- Main Area: Client Input ---
st.header("📋 Client Requirement Analysis")

input_method = st.radio("Choose Input Method:", ["Upload PDF/Document", "Project URL/Link"])

client_content = None
input_type = "text"

if input_method == "Upload PDF/Document":
    uploaded_file = st.file_uploader("Upload Client Request (PDF)", type=["pdf"])
    
    if uploaded_file:
        # Streamlit stores in RAM, PyMuPDF needs a path. We use a temp file.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        st.info("Extracting text from client file...")
        client_content = backend.extract_pdf_text(tmp_path)
        input_type = "text"
        os.remove(tmp_path)  # Clean up local temp file

elif input_method == "Project URL/Link":
    url = st.text_input("Enter Project Description Link (e.g., tender page, job post)")
    if url:
        with st.spinner("Scraping website content..."):
            client_content = backend.scrape_web_content(url)
            input_type = "text"
            st.success("Website content extracted successfully.")
            with st.expander("View Scraped Content"):
                st.text(client_content[:1000] + "...")

# --- Action Button ---
if st.button("🚀 Analyze Feasibility"):
    if not api_key:
        st.error("API Key missing.")
    elif not st.session_state.get("org_docs_text"):
        st.error("Please load Company Docs in the sidebar first.")
    elif not client_content:
        st.error("Please provide client input (File or Link).")
    else:
        with st.spinner("🤖 Agent is analyzing your capability against the requirements..."):
            try:
                response = backend.analyze_project_feasibility(
                    api_key,
                    st.session_state.org_docs_text,
                    client_content,
                )
                st.markdown("---")
                st.markdown(response)
            except Exception as e:
                st.error(f"An error occurred: {e}")