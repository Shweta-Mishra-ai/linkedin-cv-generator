import streamlit as st
import streamlit.components.v1 as components
import base64
from core.scraper import extract_pdf_text, scrape_url_text
from core.ai_engine import extract_base_cv, analyze_and_tailor_cv
from templates.cv_styles import render_cv

st.set_page_config(page_title="Pro ATS CV Generator", page_icon="🎯", layout="wide")

st.title("🎯 AI-Powered ATS CV Generator")
st.markdown("Upload your real profile data, analyze it against a JD, and generate an ATS-optimized CV.")

# --- SIDEBAR ---
st.sidebar.title("🎨 Formatting Options")
template_options = [
    "Executive Blue (Premium)", 
    "Modern Accent (Clean)", 
    "Classic Corporate",
    "Modern Sidebar (Original)",
    "Minimalist Tech (Original)"
]
selected_template = st.sidebar.selectbox("Choose CV Template:", template_options)

# --- TABS ---
tab1, tab2 = st.tabs(["📄 Step 1: Base Profile & Preview", "🎯 Step 2: ATS Tailoring & Analysis"])

if "base_cv_data" not in st.session_state:
    st.session_state.base_cv_data = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# ==========================================
# TAB 1: DATA FETCH & BASE PREVIEW
# ==========================================
with tab1:
    st.subheader("Fetch Your Profile Data")
    input_method = st.radio("Profile Source:", ("📄 Upload LinkedIn PDF (Recommended for 100% Real Data)", "🔗 Scrape via LinkedIn URL"))
    
    if input_method == "📄 Upload LinkedIn PDF (Recommended for 100% Real Data)":
        uploaded_file = st.file_uploader("Upload Profile PDF", type=['pdf'])
        if st.button("Extract Real Data", type="primary") and uploaded_file:
            with st.spinner("Extracting real data from PDF..."):
                raw_text = extract_pdf_text(uploaded_file)
                st.session_state.base_cv_data = extract_base_cv(raw_text)
                st.session_state.analysis_result = None # Reset analysis
                st.success("✅ Real Profile Data Extracted Successfully!")
                    
    elif input_method == "🔗 Scrape via LinkedIn URL":
        linkedin_url = st.text_input("Enter LinkedIn Profile URL:")
        
        if st.button("Extract Data & Generate CV", type="primary") and linkedin_url:
            with st.spinner("Fetching data and generating your CV..."):
                raw_text = scrape_url_text(linkedin_url)
                st.session_state.base_cv_data = extract_base_cv(raw_text, is_url=True)
                st.session_state.analysis_result = None
                st.success("✅ Profile Data Extracted Successfully!")

    # BASE PREVIEW & DOWNLOAD
    if st.session_state.base_cv_data:
        st.markdown("---")
        st.markdown("### 👀 Base CV Preview (Real Data)")
        base_html = render_cv(selected_template, st.session_state.base_cv_data)
        components.html(base_html, height=600, scrolling=True)
        
        b64_base = base64.b64encode(base_html.encode()).decode()
        href_base = f'<a href="data:text/html;base64,{b64_base}" download="Base_Real_CV.html" style="display:inline-block; padding:12px 24px; background-color:#1e3a8a; color:white; text-decoration:none; border-radius:5px; font-weight:bold; text-align:center; width:100%;">📥 Download Base CV</a>'
        st.markdown(href_base, unsafe_allow_html=True)

# ==========================================
# TAB 2: ATS ANALYSIS & OPTIMIZED PREVIEW
# ==========================================
with tab2:
    st.subheader("ATS Analysis & Tailoring")
    if not st.session_state.base_cv_data:
        st.warning("⚠️ Please extract your real profile data in Step 1 first.")
    else:
        jd_input = st.text_area("Paste the Target Job Description here:", height=150)
        
        if st.button("Run ATS Analysis & Optimize", type="primary") and jd_input:
            with st.spinner("AI is analyzing and optimizing your CV..."):
                st.session_state.analysis_result = analyze_and_tailor_cv(st.session_state.base_cv_data, jd_input)

        if st.session_state.analysis_result:
            analysis = st.session_state.analysis_result
            
            # SCORE METRICS
            st.markdown("### 📈 ATS Score Optimization")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Original Score", f"{analysis.get('old_ats_score', 0)}%")
            with col2:
                delta = analysis.get('new_ats_score', 0) - analysis.get('old_ats_score', 0)
                st.metric("Optimized Score", f"{analysis.get('new_ats_score', 0)}%", f"+{delta}%")
            with col3:
                st.write("**🚨 Added Keywords:**")
                st.write(", ".join(analysis.get('missing_keywords', [])))
            
            # ANALYSIS REPORT
            st.markdown("### 📊 Analysis Report")
            for pt in analysis.get('analysis_report', []):
                st.write(f"- {pt}")
            
            st.markdown("---")
            
            # OPTIMIZED PREVIEW & DOWNLOAD
            st.markdown("### 👀 Optimized CV Preview")
            tailored_html = render_cv(selected_template, analysis.get('tailored_cv', {}))
            components.html(tailored_html, height=600, scrolling=True)
            
            b64_tailored = base64.b64encode(tailored_html.encode()).decode()
            href_tailored = f'<a href="data:text/html;base64,{b64_tailored}" download="Optimized_ATS_CV.html" style="display:inline-block; padding:12px 24px; background-color:#14b8a6; color:white; text-decoration:none; border-radius:5px; font-weight:bold; text-align:center; width:100%;">📥 Download Optimized CV</a>'
            st.markdown(href_tailored, unsafe_allow_html=True)
