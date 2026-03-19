import streamlit as st
import streamlit.components.v1 as components
import base64
import json
from core.scraper import extract_pdf_text, scrape_url_text
from core.ai_engine import extract_base_cv, analyze_and_tailor_cv, generate_with_fallback
from templates.cv_styles import render_cv

# ─────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="CareerForge AI — Pro CV Builder",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
div[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 800; }
div[data-testid="stMetricDelta"] { font-size: 1.1rem; }
.stProgress > div > div { border-radius: 8px; }
.stExpander { border-radius: 10px; }
h1 { font-size: 2.2rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# SIDEBAR — TEMPLATE SELECTOR
# ─────────────────────────────────────────────────────
st.sidebar.title("🎨 CV Design")
template_options = [
    "1. Premium Two-Column (Navy & White)",
    "2. Executive Corporate (Clean & Bold)",
    "3. Creative Professional (Ribbons & Colors)",
    "4. Minimalist Clean (Kinsley Morrison)",
    "5. Modern Single Column (Teal Accent)",
    "6. Academic Structured (Classic)",
    "7. Dark Premium (Gold & Charcoal)"
]
selected_template = st.sidebar.selectbox("Choose a Template:", template_options)
st.sidebar.markdown("---")
st.sidebar.info("📋 **Steps:**\n1. Upload your CV/Profile\n2. Get a beautifully formatted CV\n3. *(Optional)* Add a Job Description for deep ATS analysis & improved CV")

# ─────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────
for key in ["base_cv_data", "analysis_result", "jd_text", "cover_letter", "interview_prep"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "jd_text" else ""

# ─────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────
st.markdown("# 🎯 CareerForge AI")
st.markdown("Upload any CV or profile → get an **ATS-optimised, beautifully designed CV** instantly. Add a Job Description for a **deep gap analysis + tailored CV**.")

st.markdown("---")

# ─────────────────────────────────────────────────────
# STEP 1 — PROFILE INPUT & CV GENERATION
# ─────────────────────────────────────────────────────
with st.expander("📄 **STEP 1 — Upload Your Profile / CV**", expanded=True):
    input_method = st.radio(
        "Choose Input Method:",
        ("📄 Upload CV (PDF)", "🔗 Enter Profile URL (LinkedIn / Portfolio)", "📝 Paste Text / Chrome Extension Data"),
        horizontal=True
    )

    col_input, col_btn = st.columns([4, 1])

    with col_input:
        if input_method == "📄 Upload CV (PDF)":
            uploaded_file = st.file_uploader("Upload your CV PDF", type=["pdf"], label_visibility="collapsed")
        elif input_method == "🔗 Enter Profile URL (LinkedIn / Portfolio)":
            url_input = st.text_input("Enter URL:", placeholder="https://linkedin.com/in/yourprofile or https://yourportfolio.com")
        else:
            pasted_text = st.text_area("Paste your profile text or JSON from the Chrome Extension:", height=160)

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button("⚡ Generate CV", type="primary", use_container_width=True)

    if generate_btn:
        raw_text = None
        is_url = False
        try:
            with st.spinner("🔍 Extracting and structuring your profile data…"):
                if input_method == "📄 Upload CV (PDF)":
                    if not uploaded_file:
                        st.error("❌ Please upload a PDF file first.")
                        st.stop()
                    raw_text = extract_pdf_text(uploaded_file)

                elif input_method == "🔗 Enter Profile URL (LinkedIn / Portfolio)":
                    if not url_input:
                        st.error("❌ Please enter a URL.")
                        st.stop()
                    raw_text = scrape_url_text(url_input)
                    is_url = True

                else:
                    if not pasted_text:
                        st.error("❌ Please paste your profile text.")
                        st.stop()
                    raw_text = pasted_text

                if not raw_text or len(raw_text.strip()) < 50:
                    st.error("❌ Not enough text was extracted. Please try another input method.")
                    st.stop()

            with st.spinner("🧠 AI is building your professional CV…"):
                st.session_state.base_cv_data = extract_base_cv(raw_text, is_url=is_url)
                st.session_state.analysis_result = None  # Reset any previous ATS analysis

            st.success("✅ CV generated successfully! Scroll down to preview and download.")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ─────────────────────────────────────────────────────
# STEP 1 RESULT — CV PREVIEW
# ─────────────────────────────────────────────────────
if st.session_state.base_cv_data:
    cv_data = st.session_state.base_cv_data

    # Quick data check
    if not cv_data.get("name") or cv_data.get("name") == "Candidate":
        st.warning("⚠️ Name could not be extracted. The CV was still generated with available data.")

    st.markdown("### 👀 Your Professional CV Preview")
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.info(f"**👤 Name:** {cv_data.get('name', 'N/A')}")
    with col_info2:
        skills_count = len([s for s in cv_data.get('skills', '').split(',') if s.strip()])
        st.info(f"**🛠️ Skills Found:** {skills_count}")
    with col_info3:
        has_proj = bool(cv_data.get("projects", ""))
        st.info(f"**🚀 Projects:** {'Yes ✅' if has_proj else 'None found'}")

    base_html = render_cv(selected_template, cv_data)
    components.html(base_html, height=750, scrolling=True)

    b64 = base64.b64encode(base_html.encode()).decode()
    st.markdown(
        f'<a href="data:text/html;base64,{b64}" download="CareerForge_CV.html" '
        f'style="display:inline-block;padding:12px 28px;background:#1e3a8a;color:white;'
        f'text-decoration:none;border-radius:8px;font-weight:700;font-size:15px;width:100%;text-align:center;margin-top:8px;">'
        f'📥 Download CV (HTML — Print to PDF)</a>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ─────────────────────────────────────────────────────
    # STEP 2 — ATS ANALYSIS (OPTIONAL)
    # ─────────────────────────────────────────────────────
    with st.expander("🎯 **STEP 2 (Optional) — Paste Job Description for ATS Analysis & Tailored CV**", expanded=True):
        jd_input = st.text_area(
            "Paste the full Job Description here:",
            height=200,
            value=st.session_state.jd_text,
            placeholder="Paste the full JD from LinkedIn, Naukri, Indeed, or any job portal…"
        )
        ats_btn = st.button("🔬 Run Deep ATS Analysis", type="primary", use_container_width=False)

        if ats_btn:
            if not jd_input or len(jd_input.strip()) < 100:
                st.error("❌ Please paste a full Job Description (at least a few sentences).")
            else:
                st.session_state.jd_text = jd_input
                with st.spinner("🧠 AI is analysing your CV against the JD and tailoring it…"):
                    try:
                        st.session_state.analysis_result = analyze_and_tailor_cv(cv_data, jd_input)
                        st.success("✅ Analysis complete!")
                    except Exception as e:
                        st.error(f"❌ ATS Analysis failed: {str(e)}")

    # ─────────────────────────────────────────────────────
    # STEP 2 RESULT — ATS REPORT + TAILORED CV
    # ─────────────────────────────────────────────────────
    if st.session_state.analysis_result:
        analysis = st.session_state.analysis_result
        tailored = analysis.get("tailored_cv", {})

        st.markdown("---")
        st.markdown("## 📊 Deep ATS Analysis Report")

        # ── SCORE ROW ──
        col1, col2, col3, col4 = st.columns(4)
        old_score = analysis.get("old_ats_score", 0)
        new_score = analysis.get("new_ats_score", 0)
        delta = new_score - old_score
        missing_count = len(analysis.get("missing_keywords", []))

        col1.metric("📄 Original ATS Score", f"{old_score}%")
        col2.metric("✅ Tailored ATS Score", f"{new_score}%", f"+{delta}%")
        col3.metric("🚨 Missing Keywords", str(missing_count))
        col4.metric("🔧 Improvements Made", str(len(analysis.get("improvements_made", []))))

        # ── SECTION SCORES ──
        section_scores = analysis.get("section_scores", {})
        if section_scores:
            st.markdown("#### 📈 Section-by-Section Breakdown")
            s_cols = st.columns(len(section_scores))
            for i, (sec, score) in enumerate(section_scores.items()):
                s_cols[i].metric(sec.replace("_", " ").title(), f"{score}%")

        st.markdown("---")

        # ── TWO COLUMN DETAILS ──
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("#### 🚨 Missing Keywords (Add These!)")
            for kw in analysis.get("missing_keywords", []):
                st.error(f"❌ {kw}")

            st.markdown("#### 📋 CV Formatting Issues")
            for issue in analysis.get("formatting_issues", []):
                st.warning(f"⚠️ {issue}")

        with col_r:
            st.markdown("#### 🎯 Keyword Match Analysis")
            st.info(analysis.get("keyword_match_details", "N/A"))

            hallucination_msg = analysis.get("hallucination_check", "Unknown")
            st.markdown("#### 🛡️ Integrity Check")
            if "Safe" in hallucination_msg:
                st.success(f"✅ {hallucination_msg}")
            else:
                st.warning(f"⚠️ {hallucination_msg}")

        st.markdown("---")

        # ── IMPROVEMENTS MADE ──
        improvements = analysis.get("improvements_made", [])
        if improvements:
            st.markdown("#### ✏️ What Was Improved in Your CV")
            for i, imp in enumerate(improvements, 1):
                st.markdown(f"> **{i}.** {imp}")

        # ── STRATEGIC INSIGHTS ──
        with st.expander("💡 Strategic Insights & Recommendations"):
            for pt in analysis.get("analysis_report", []):
                st.markdown(f"- {pt}")

        st.markdown("---")

        # ── TAILORED CV PREVIEW ──
        st.markdown("### 🏆 Your Tailored CV (Optimised for this Job)")
        if tailored:
            tailored_html = render_cv(selected_template, tailored)
            components.html(tailored_html, height=750, scrolling=True)
            b64_t = base64.b64encode(tailored_html.encode()).decode()
            st.markdown(
                f'<a href="data:text/html;base64,{b64_t}" download="CareerForge_Tailored_CV.html" '
                f'style="display:inline-block;padding:12px 28px;background:#0d9488;color:white;'
                f'text-decoration:none;border-radius:8px;font-weight:700;font-size:15px;width:100%;text-align:center;margin-top:8px;">'
                f'📥 Download Tailored CV (HTML — Print to PDF)</a>',
                unsafe_allow_html=True
            )
        else:
            st.error("❌ Tailored CV could not be generated. Please try running the analysis again.")

        st.markdown("---")

        # ── CAREER TOOLS ──
        st.markdown("## 🚀 Career Tools")
        saved_jd = st.session_state.get("jd_text", "")
        col_cl, col_prep = st.columns(2)

        with col_cl:
            st.markdown("### ✉️ Cover Letter")
            if st.button("Generate Cover Letter", use_container_width=True):
                with st.spinner("Writing your personalised cover letter…"):
                    try:
                        tv = json.dumps(tailored or cv_data)
                        cl_prompt = f"""Write a professional, personalised cover letter (3 paragraphs) based ONLY on the candidate's actual CV and the target Job Description.
Paragraph 1: Strong opening, why this role & company.
Paragraph 2: 2-3 specific achievements from the CV that match the JD requirements.
Paragraph 3: Confident closing.
Do NOT invent facts. Output only the letter text.

CV: {tv[:4000]}
JD: {saved_jd[:4000]}"""
                        st.session_state.cover_letter = generate_with_fallback(cl_prompt, temp=0.4)
                    except Exception as e:
                        st.error(f"Failed: {e}")

            if st.session_state.cover_letter:
                st.text_area("Your Cover Letter:", st.session_state.cover_letter, height=380)

        with col_prep:
            st.markdown("### 🎤 Interview Prep")
            if st.button("Generate Interview Questions", use_container_width=True):
                with st.spinner("Preparing interview questions based on your gaps…"):
                    try:
                        missing_kw = ", ".join(analysis.get("missing_keywords", []))
                        tv = json.dumps(tailored or cv_data)
                        ip_prompt = f"""You are a senior technical interviewer. Generate 5 targeted interview questions for this candidate applying to this role.
Focus especially on these skill gaps: {missing_kw}
Format each as:
**Q[N]: [Question]**
*Answer Strategy:* [How to answer using the candidate's actual background]

CV: {tv[:3000]}
JD: {saved_jd[:3000]}"""
                        st.session_state.interview_prep = generate_with_fallback(ip_prompt, temp=0.4)
                    except Exception as e:
                        st.error(f"Failed: {e}")

            if st.session_state.interview_prep:
                st.markdown(st.session_state.interview_prep)
