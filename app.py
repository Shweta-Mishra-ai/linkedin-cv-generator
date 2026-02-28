import streamlit as st
import streamlit.components.v1 as components
import base64
from core.scraper import extract_pdf_text, scrape_url_text
from core.ai_engine import extract_base_cv, analyze_and_tailor_cv
from templates.cv_styles import render_cv

st.set_page_config(page_title="Pro ATS CV Generator", page_icon="🎯", layout="wide")

st.title("🎯 AI-Powered ATS CV Generator")
st.markdown("Extract your profile, analyze it against a JD, and generate a tailored CV with premium templates.")

# --- SENIOR DEV TRICK: CACHING API CALLS ---
# This prevents the "ResourceExhausted" error by not hitting the API unnecessarily
@st.cache_data(show_spinner=False)
def cached_extract_base(raw_text):
    return extract_base_cv(raw_text)

@st.cache_data(show_spinner=False)
def cached_analyze(base_cv_data, jd_input):
    return analyze_and_tailor_cv(base_cv_data, jd_input)

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

with tab1:
    st.subheader("Upload Your Profile")
    input_method = st.radio("Profile Source:", ("📄 Upload LinkedIn PDF (Recommended)", "🔗 Scrape via LinkedIn URL"))
    
    if input_method == "📄 Upload LinkedIn PDF (Recommended)":
        uploaded_file = st.file_uploader("Upload Profile PDF", type=['pdf'])
        if st.button("Extract Base CV", type="primary") and uploaded_file:
            with st.spinner("Analyzing PDF..."):
                try:
                    raw_text = extract_pdf_text(uploaded_file)
                    st.session_state.base_cv_data = cached_extract_base(raw_text)
                    st.success("✅ Profile Extracted Successfully!")
                except Exception as e:
                    st.error(f"API Error: Please wait a minute and try again. (Details: {e})")
                    
    elif input_method == "🔗 Scrape via LinkedIn URL":
        linkedin_url = st.text_input("Enter LinkedIn Profile URL:")
        st.caption("Note: LinkedIn blocks direct scraping. The AI will intelligently build a highly professional profile based on your public name.")
        if st.button("Extract Base CV", type="primary") and linkedin_url:
            with st.spinner("Intelligently extracting & building a full professional profile..."):
                try:
                    raw_text = scrape_url_text(linkedin_url)
                    st.session_state.base_cv_data = cached_extract_base(raw_text)
                    st.success("✅ Profile Built Successfully!")
                except Exception as e:
                    st.error(f"API Error: Please wait a minute and try again. (Details: {e})")

    if st.session_state.base_cv_data:
        st.markdown("---")
        st.markdown("### 👀 Base CV Preview")
        base_html = render_cv(selected_template, st.session_state.base_cv_data)
        components.html(base_html, height=600, scrolling=True)
        
        st.markdown("---")
        b64_base = base64.b64encode(base_html.encode()).decode()
        href_base = f'<a href="data:text/html;base64,{b64_base}" download="Base_CV.html" style="display:inline-block; padding:12px 24px; background-color:#1e3a8a; color:white; text-decoration:none; border-radius:5px; font-weight:bold; text-align:center; width:100%;">📥 Download Base CV</a>'
        st.markdown(href_base, unsafe_allow_html=True)

with tab2:
    st.subheader("Tailor to a Job Description")
    if not st.session_state.base_cv_data:
        st.warning("⚠️ Please extract your base profile in Step 1 first.")
    else:
        jd_input = st.text_area("Paste the Target Job Description here:", height=150)
        
        if st.button("Analyze, Tailor & Preview CV", type="primary") and jd_input:
            with st.spinner("AI is analyzing ATS score and crafting your perfect CV... This may take up to 15 seconds."):
                try:
                    # Using cached version to save API quota
                    st.session_state.analysis_result = cached_analyze(st.session_state.base_cv_data, jd_input)
                except Exception as e:
                    st.error(f"API Error: Too many requests. Google API needs a break. Please wait 30 seconds and click again. (Details: {e})")

        # If we have results, show them (even if button wasn't just clicked, so template changes work)
        if st.session_state.analysis_result:
            analysis_result = st.session_state.analysis_result
            
            # 1. SHOW THE SCORE
            st.markdown("### 📈 ATS Score Improvement")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Original Score", value=f"{analysis_result.get('old_ats_score', 0)}%")
            with col2:
                delta_val = analysis_result.get('new_ats_score', 0) - analysis_result.get('old_ats_score', 0)
                st.metric(label="New Tailored Score", value=f"{analysis_result.get('new_ats_score', 0)}%", delta=f"+{delta_val}%")
            with col3:
                st.write("**🚨 Added Keywords:**")
                st.write(", ".join(analysis_result.get('missing_keywords', [])))
            
            st.markdown("---")
            
            # 2. SHOW ANALYSIS REPORT
            st.markdown("### 📊 Detailed Analysis & Improvement Report")
            for point in analysis_result.get('analysis_report', ["Analysis report unavailable."]):
                st.markdown(f"- {point}")
            
            st.markdown("---")
            
            # 3. SHOW THE LIVE PREVIEW
            st.markdown("### 👀 Live Tailored CV Preview")
            st.info(f"Currently viewing: **{selected_template}**. You can change templates in the sidebar and it will update instantly without using API quota!")
            
            tailored_html = render_cv(selected_template, analysis_result.get('tailored_cv', {}))
            components.html(tailored_html, height=600, scrolling=True)
            
            st.markdown("---")
            
            # 4. DOWNLOAD BUTTON
            b64_tailored = base64.b64encode(tailored_html.encode()).decode()
            href_tailored = f'<a href="data:text/html;base64,{b64_tailored}" download="Tailored_ATS_CV.html" style="display:inline-block; padding:12px 24px; background-color:#14b8a6; color:white; text-decoration:none; border-radius:5px; font-weight:bold; text-align:center; width:100%;">📥 I am Satisfied - Download My ATS-Optimized CV</a>'
            st.markdown(href_tailored, unsafe_allow_html=True)
