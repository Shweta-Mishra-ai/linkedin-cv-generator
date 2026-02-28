import streamlit as st
import base64
from core.scraper import extract_pdf_text, scrape_url_text, get_linkedin_fallback_data
from core.ai_engine import extract_base_cv, analyze_and_tailor_cv
from templates.cv_styles import render_cv

st.set_page_config(page_title="Pro ATS CV Generator", page_icon="🎯", layout="wide")

st.title("🎯 AI-Powered ATS CV Generator")
st.markdown("Extract your LinkedIn profile, analyze it against a Job Description, and generate a perfectly tailored CV in 3 beautiful templates.")

# --- SIDEBAR: TEMPLATE SELECTION ---
st.sidebar.title("🎨 Formatting Options")
selected_template = st.sidebar.selectbox("Choose CV Template:", ["Modern Sidebar", "Classic Corporate", "Minimalist Tech"])
st.sidebar.markdown("---")
st.sidebar.info("Tip: Once generated, open the HTML file and press Ctrl+P to save as a highly formatted PDF.")

# --- MAIN UI TABS ---
tab1, tab2 = st.tabs(["📄 Step 1: Base Profile", "🎯 Step 2: ATS Tailoring (Optional)"])

# State management to pass data between tabs
if "base_cv_data" not in st.session_state:
    st.session_state.base_cv_data = None

with tab1:
    st.subheader("Upload Your Profile")
    input_method = st.radio("Profile Source:", ("📄 Upload LinkedIn PDF", "🔗 Scrape via LinkedIn URL"))
    
    if input_method == "📄 Upload LinkedIn PDF":
        uploaded_file = st.file_uploader("Upload Profile PDF", type=['pdf'])
        if st.button("Extract Base CV", type="primary") and uploaded_file:
            with st.spinner("Analyzing PDF..."):
                raw_text = extract_pdf_text(uploaded_file)
                try:
                    st.session_state.base_cv_data = extract_base_cv(raw_text)
                    st.success("✅ Profile Extracted Successfully! You can now generate it or move to Step 2 for ATS Tailoring.")
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    elif input_method == "🔗 Scrape via LinkedIn URL":
        linkedin_url = st.text_input("Enter LinkedIn Profile URL:")
        if st.button("Extract Base CV", type="primary") and linkedin_url:
            with st.spinner("Bypassing security & scraping..."):
                raw_text = scrape_url_text(linkedin_url)
                if len(raw_text) < 100 or "security" in raw_text.lower():
                    raw_text = get_linkedin_fallback_data(linkedin_url)
                try:
                    st.session_state.base_cv_data = extract_base_cv(raw_text)
                    st.success("✅ Profile Extracted Successfully! You can now generate it or move to Step 2 for ATS Tailoring.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Generate Base CV Button
    if st.session_state.base_cv_data:
        st.markdown("---")
        final_html = render_cv(selected_template, st.session_state.base_cv_data)
        b64 = base64.b64encode(final_html.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="Base_CV.html" style="display:inline-block; padding:10px 20px; background-color:#4CAF50; color:white; text-decoration:none; border-radius:5px;">📥 Download Base CV</a>'
        st.markdown(href, unsafe_allow_html=True)

with tab2:
    st.subheader("Tailor to a Job Description")
    if not st.session_state.base_cv_data:
        st.warning("⚠️ Please extract your base profile in Step 1 first.")
    else:
        jd_input = st.text_area("Paste the Target Job Description here:", height=150)
        
        if st.button("Analyze & Auto-Tailor CV", type="primary") and jd_input:
            with st.spinner("AI is analyzing ATS score and tailoring your CV..."):
                try:
                    analysis_result = analyze_and_tailor_cv(st.session_state.base_cv_data, jd_input)
                    
                    # Display Results
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric(label="ATS Match Score", value=f"{analysis_result['ats_score']}%")
                        st.progress(analysis_result['ats_score'] / 100)
                    with col2:
                        st.write("**🚨 Missing Keywords (Now injected into new CV):**")
                        st.write(", ".join(analysis_result['missing_keywords']))
                    
                    st.markdown("### 💡 Improvement Suggestions")
                    for imp in analysis_result['improvements']:
                        st.write(f"- {imp}")
                        
                    st.markdown("---")
                    st.success("✨ Your New ATS-Tailored CV is Ready!")
                    
                    # Generate Tailored CV
                    tailored_html = render_cv(selected_template, analysis_result['tailored_cv'])
                    b64_tailored = base64.b64encode(tailored_html.encode()).decode()
                    href_tailored = f'<a href="data:text/html;base64,{b64_tailored}" download="Tailored_ATS_CV.html" style="display:inline-block; padding:12px 24px; background-color:#008CBA; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">📥 Download Tailored CV</a>'
                    st.markdown(href_tailored, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error during analysis: {e}")
