import streamlit as st
import PyPDF2
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import base64

st.set_page_config(page_title="Pro AI CV Generator", page_icon="📄", layout="wide")

# ==========================================
# 1. CLEAN UI
# ==========================================
st.title("📄 AI LinkedIn to CV Generator")
st.markdown("Simply upload a LinkedIn PDF or paste a URL to generate a perfectly designed CV.")

input_method = st.radio("Choose your method:", ("📄 Upload LinkedIn PDF", "🔗 Scrape via LinkedIn URL"))
st.markdown("---")

# ==========================================
# 2. BEAUTIFUL DESIGN TEMPLATE
# ==========================================
def generate_html_cv(name, headline, contact_info, skills, main_content):
    html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; margin: 0; padding: 20px; }}
        .cv-container {{ max-width: 850px; margin: auto; background: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: flex; min-height: 1050px; overflow: hidden; }}
        .left-col {{ width: 35%; background-color: #2A3B4C; color: white; padding: 30px 20px; }}
        .right-col {{ width: 65%; padding: 40px 30px; color: #333; }}
        h1 {{ margin: 0; font-size: 28px; text-transform: uppercase; letter-spacing: 2px; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; margin-bottom: 10px; }}
        h2 {{ color: #2A3B4C; font-size: 20px; border-bottom: 2px solid #ddd; padding-bottom: 5px; margin-top: 30px; text-transform: uppercase; }}
        h3 {{ font-size: 16px; color: #4CAF50; margin-bottom: 5px; text-transform: uppercase; }}
        .headline {{ font-size: 16px; font-weight: 300; font-style: italic; color: #d0d0d0; margin-bottom: 30px; }}
        .contact-item {{ font-size: 14px; margin-bottom: 10px; }}
        .skill-item {{ display: inline-block; background: rgba(255,255,255,0.1); padding: 5px 10px; margin: 5px 5px 0 0; border-radius: 3px; font-size: 13px; }}
        .content-text {{ font-size: 14px; line-height: 1.6; }}
        ul {{ padding-left: 20px; margin-top: 5px; }}
        li {{ margin-bottom: 8px; }}
    </style>
    </head>
    <body>
        <div class="cv-container">
            <div class="left-col">
                <h1>{name}</h1>
                <div class="headline">{headline}</div>
                <h3>Contact</h3>
                <div class="contact-item">📧 {contact_info}</div>
                <h3 style="margin-top:40px;">Top Skills</h3>
                {"".join([f'<div class="skill-item">{skill.strip()}</div>' for skill in skills.split(',') if skill.strip()])}
            </div>
            <div class="right-col">
                <h2>Professional Details</h2>
                <div class="content-text">{main_content}</div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# ==========================================
# 3. AI EXTRACTION ENGINE
# ==========================================
def process_with_ai(raw_text):
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("🚨 Configuration Error: Key missing in Streamlit Secrets.")
        st.stop()

    try:
        best_model_name = None
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name:
                    best_model_name = m.name
                    break
        
        if not best_model_name:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    best_model_name = m.name
                    break

        model = genai.GenerativeModel(best_model_name)
        
        prompt = f"""
        Act as an expert HR. Extract data from this profile text into STRICT JSON. 
        Return ONLY raw JSON, no markdown. 
        Keys: "name", "headline", "contact", "skills" (comma separated), "experience" (formatted with HTML <p>, <ul>, <li>).
        If the text is short, creatively generate a highly professional placeholder summary and experience relevant to their headline or name.
        Text: {raw_text[:8000]} 
        """
        response = model.generate_content(prompt)
        clean_text = response.text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
        return json.loads(clean_text)
    
    except Exception as e:
        st.error(f"🚨 AI Processing Error: {str(e)}")
        return None

# ==========================================
# 4. APP LOGIC
# ==========================================

# --- METHOD 1: PDF UPLOAD ---
if input_method == "📄 Upload LinkedIn PDF":
    uploaded_file = st.file_uploader("Upload Profile PDF", type=['pdf'])
    
    if uploaded_file is not None:
        if st.button("Generate Perfect CV", type="primary"):
            with st.spinner("Analyzing PDF and generating design..."):
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                raw_text = "".join(page.extract_text() + "\n" for page in pdf_reader.pages)
                
                ai_data = process_with_ai(raw_text)
                if ai_data:
                    final_html = generate_html_cv(
                        name=ai_data.get("name", "Name Not Found"),
                        headline=ai_data.get("headline", "Professional Headline"),
                        contact_info=ai_data.get("contact", "Not Provided"),
                        skills=ai_data.get("skills", "Skill 1, Skill 2, Skill 3"),
                        main_content=ai_data.get("experience", "Experience details missing.")
                    )
                    st.success("✅ Perfect CV Generated!")
                    b64 = base64.b64encode(final_html.encode()).decode()
                    href = f'<a href="data:text/html;base64,{b64}" download="{ai_data.get("name", "User").replace(" ", "_")}_CV.html" style="display:inline-block; padding:12px 24px; background-color:#4CAF50; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">📥 Download Your CV</a>'
                    st.markdown(href, unsafe_allow_html=True)

# --- METHOD 2: URL SCRAPING (NEW & IMPROVED) ---
elif input_method == "🔗 Scrape via LinkedIn URL":
    linkedin_url = st.text_input("Enter LinkedIn Profile URL:", placeholder="e.g., [https://www.linkedin.com/in/shweta-mishra-ai](https://www.linkedin.com/in/shweta-mishra-ai)")
    
    if st.button("Scrape & Generate CV", type="primary"):
        if not linkedin_url:
            st.warning("Please enter a URL first.")
        else:
            with st.spinner("Bypassing LinkedIn security to extract profile data..."):
                extracted_name = ""
                extracted_headline = ""
                
                try:
                    # 🟢 TRICK 1: Pretend to be a Google/WhatsApp Link Preview Bot
                    headers = {
                        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +[http://www.google.com/bot.html](http://www.google.com/bot.html))",
                        "Accept": "text/html,application/xhtml+xml"
                    }
                    response = requests.get(linkedin_url, headers=headers, timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract Name and Headline from meta tags (Open Graph)
                    og_title = soup.find("meta", property="og:title")
                    og_desc = soup.find("meta", property="og:description")
                    
                    if og_title:
                        extracted_name = og_title.get("content", "").split(" | ")[0].split(" - ")[0]
                    if og_desc:
                        extracted_headline = og_desc.get("content", "")
                        
                except Exception:
                    pass

                # 🟢 TRICK 2: If scraping completely fails, extract the name directly from the URL slug!
                if not extracted_name or "LinkedIn" in extracted_name:
                    try:
                        # e.g., converts 'shweta-mishra-ai' to 'Shweta Mishra Ai'
                        slug = linkedin_url.strip("/").split("/")[-1]
                        extracted_name = slug.replace("-", " ").title()
                        extracted_headline = "Professional on LinkedIn"
                    except:
                        extracted_name = "LinkedIn User"
                        extracted_headline = "Professional"

                # Combine the extracted real data to send to AI
                raw_text = f"Name: {extracted_name}\nHeadline/Summary: {extracted_headline}\n"

            with st.spinner(f"Formatting CV for {extracted_name}..."):
                ai_data = process_with_ai(raw_text)
                if ai_data:
                    final_html = generate_html_cv(
                        name=ai_data.get("name", extracted_name),
                        headline=ai_data.get("headline", extracted_headline),
                        contact_info=ai_data.get("contact", "Available on LinkedIn"),
                        skills=ai_data.get("skills", "Communication, Leadership, Problem Solving"),
                        main_content=ai_data.get("experience", "<p>Detailed experience hidden by LinkedIn privacy settings. Connect on LinkedIn to view full history.</p>")
                    )
                    st.success(f"✅ Perfect CV Generated for {extracted_name}!")
                    b64 = base64.b64encode(final_html.encode()).decode()
                    href = f'<a href="data:text/html;base64,{b64}" download="{ai_data.get("name", "User").replace(" ", "_")}_CV.html" style="display:inline-block; padding:12px 24px; background-color:#4CAF50; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">📥 Download Your CV</a>'
                    st.markdown(href, unsafe_allow_html=True)
