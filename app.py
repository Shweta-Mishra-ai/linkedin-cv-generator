import streamlit as st
import streamlit.components.v1 as components
import base64
from core.scraper import extract_pdf_text, scrape_url_text
from core.ai_engine import extract_base_cv, analyze_and_tailor_cv
from templates.cv_styles import render_cv

st.set_page_config(page_title="Pro ATS CV Generator", page_icon="🎯", layout="wide")

st.title("🎯 AI-Powered ATS CV Generator")
st.markdown("Extract your profile, analyze it against a JD, and generate a tailored CV with premium templates.")

# --- SIDEBAR ---
st.sidebar.title("🎨 Formatting Options")
selected_template = st.sidebar.selectbox("Choose CV Template:", ["Executive Blue (Premium)", "Modern Accent (Clean)", "Classic Corporate"])

# --- TABS ---
tab1, tab2 = st.tabs(["📄 Step 1: Base Profile", "🎯 Step 2: ATS Tailoring & Preview"])

if "base_cv_data" not in st.session_state:
    st.session_state.base_cv_data = None

with tab1:
    st.subheader("Upload Your Profile")
    input_method = st.radio("Profile Source:", ("📄 Upload LinkedIn PDF (Recommended)", "🔗 Scrape via LinkedIn URL"))
    
    if input_method == "📄 Upload LinkedIn PDF (Recommended)":
        uploaded_file = st.file_uploader("Upload Profile PDF", type=['pdf'])
        if st.button("Extract Base CV", type="primary") and uploaded_file:
            with st.spinner("Analyzing PDF..."):
                try:
                    raw_text = extract_pdf_text(uploaded_file)
                    st.session_state.base_cv_data = extract_base_cv(raw_text)
                    st.success("✅ Profile Extracted Successfully! Move to Step 2.")
                except Exception as e:
                    st.error(f"Error: {e}. Please check your API Key.")
                    
    elif input_method == "🔗 Scrape via LinkedIn URL":
        linkedin_url = st.text_input("Enter LinkedIn Profile URL:")
        st.caption("Note: LinkedIn blocks direct scraping. The app will smartly extract your name from the URL if blocked.")
        if st.button("Extract Base CV", type="primary") and linkedin_url:
            with st.spinner("Scraping & intelligently extracting data..."):
                try:
                    raw_text = scrape_url_text(linkedin_url)
                    st.session_state.base_cv_data = extract_base_cv(raw_text)
                    st.success("✅ Profile Extracted Successfully! Move to Step 2.")
                except Exception as e:
                    st.error(f"Error: {e}. Please check your API Key.")

with tab2:
    st.subheader("Tailor to a Job Description")
    if not st.session_state.base_cv_data:
        st.warning("⚠️ Please extract your base profile in Step 1 first.")
    else:
        jd_input = st.text_area("Paste the Target Job Description here:", height=150)
        
        if st.button("Analyze, Tailor & Preview CV", type="primary") and jd_input:
            with st.spinner("AI is analyzing ATS score and crafting your perfect CV..."):
                try:
                    analysis_result = analyze_and_tailor_cv(st.session_state.base_cv_data, jd_input)
                    
                    # 1. SHOW THE SCORE IMPROVEMENT
                    st.markdown("### 📈 ATS Score Improvement")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="Original Score", value=f"{analysis_result['old_ats_score']}%")
                    with col2:
                        st.metric(label="New Tailored Score", value=f"{analysis_result['new_ats_score']}%", delta=f"+{analysis_result['new_ats_score'] - analysis_result['old_ats_score']}%")
                    with col3:
                        st.write("**🚨 Added Keywords:**")
                        st.write(", ".join(analysis_result['missing_keywords']))
                    
                    st.markdown("---")
                    
                    # 2. SHOW THE LIVE PREVIEW
                    st.markdown("### 👀 Live CV Preview")
                    st.info(f"Currently viewing: **{selected_template}**. You can change the template from the sidebar.")
                    
                    tailored_html = render_cv(selected_template, analysis_result['tailored_cv'])
                    
                    # Render HTML directly in Streamlit
                    components.html(tailored_html, height=600, scrolling=True)
                    
                    st.markdown("---")
                    
                    # 3. DOWNLOAD BUTTON
                    b64_tailored = base64.b64encode(tailored_html.encode()).decode()
                    href_tailored = f'<a href="data:text/html;base64,{b64_tailored}" download="Tailored_ATS_CV.html" style="display:inline-block; padding:12px 24px; background-color:#1e3a8a; color:white; text-decoration:none; border-radius:5px; font-weight:bold; text-align:center; width:100%;">📥 I am Satisfied - Download My CV</a>'
                    st.markdown(href_tailored, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error during analysis: {e}")
