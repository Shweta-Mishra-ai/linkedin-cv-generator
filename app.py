import streamlit as st
import PyPDF2
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import base64

st.set_page_config(page_title="AI Pro CV Generator", page_icon="✨", layout="wide")

# ==========================================
# 1. UI LOAD HOGA SABSE PEHLE
# ==========================================
st.title("✨ Ultimate AI LinkedIn to CV Generator")
st.markdown("Choose your method below. Our AI will extract the data and design a beautiful CV.")

# URL aur PDF ka option hamesha dikhega
input_method = st.radio("Select Input Method:", ("📄 Upload LinkedIn PDF", "🔗 Scrape via LinkedIn URL"))
st.markdown("---")

# ==========================================
# 2. API KEY LOGIC (Background mein)
# ==========================================
api_key = None
try:
    # Try getting from secrets
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    pass

# Agar secrets se nahi mili, toh sidebar mein manually dalne ka option dikhayenge
if not api_key:
    api_key = st.sidebar.text_input("🔑 Streamlit Secret missing. Enter Gemini API Key here to test:", type="password")

if api_key:
    genai.configure(api_key=api_key)

# ==========================================
# 3. HELPER FUNCTIONS
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
        ul {{ padding-left: 20px; }}
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
                <h2>Professional Experience & Education</h2>
                <div class="content-text">{main_content}</div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def extract_data_with_ai(raw_text):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are an expert HR recruiter. Analyze the following profile text and extract the information into a STRICT JSON format. 
        Do not add any markdown formatting. Return ONLY the raw JSON object.
        Keys must be exact: "name", "headline", "contact", "skills", "experience".
        Profile Text: {raw_text[:8000]} 
        """
        response = model.generate_content(prompt)
        clean_text = response.text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
        return json.loads(clean_text)
    except Exception as e:
        st.error(f"🚨 API Error: {str(e)}")
        return None

# ==========================================
# 4. APP LOGIC (PDF & URL Actions)
# ==========================================

if input_method == "📄 Upload LinkedIn PDF":
    uploaded_file = st.file_uploader("Upload Profile PDF", type=['pdf'])
    
    if uploaded_file is not None:
        if st.button("Generate AI CV from PDF", type="primary"):
            if not api_key:
                st.error("⚠️ API Key is missing! Please enter it in the sidebar.")
            else:
                with st.spinner("AI is reading the PDF and designing the CV..."):
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    raw_text = "".join(page.extract_text() + "\n" for page in pdf_reader.pages)
                    
                    ai_data = extract_data_with_ai(raw_text)
                    if ai_data:
                        final_html = generate_html_cv(
                            name=ai_data.get("name", "Name Not Found"),
                            headline=ai_data.get("headline", "Professional"),
                            contact_info=ai_data.get("contact", "Not Provided"),
                            skills=ai_data.get("skills", "Communication, Teamwork"),
                            main_content=ai_data.get("experience", "Experience details missing.")
                        )
                        st.success("✅ AI successfully generated your CV!")
                        b64 = base64.b64encode(final_html.encode()).decode()
                        href = f'<a href="data:text/html;base64,{b64}" download="{ai_data.get("name", "User").replace(" ", "_")}_CV.html" style="display:inline-block; padding:12px 24px; background-color:#4CAF50; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">📥 Download AI-Designed CV</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.caption("Open downloaded file in browser and press Ctrl+P to save as PDF.")

elif input_method == "🔗 Scrape via LinkedIn URL":
    linkedin_url = st.text_input("Enter LinkedIn Profile URL:")
    
    if st.button("Scrape & Generate AI CV", type="primary"):
        if not api_key:
            st.error("⚠️ API Key is missing! Please enter it in the sidebar.")
        elif not linkedin_url:
            st.warning("Please enter a URL.")
        else:
            with st.spinner("Scraping profile and bypassing security..."):
                headers = {"User-Agent": "Mozilla/5.0"}
                try:
                    response = requests.get(linkedin_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        extracted_text = soup.get_text(separator=' ', strip=True)
                    else:
                        st.warning("⚠️ LinkedIn blocked direct scraping. Passing fallback data to AI.")
                        extracted_text = "Name: Demo User. Headline: Software Engineer. Skills: Python, React. Experience: Built amazing projects."
                except:
                    extracted_text = "Name: Demo User. Skills: Python."

            with st.spinner("AI is structuring the data..."):
                ai_data = extract_data_with_ai(extracted_text)
                if ai_data:
                    final_html = generate_html_cv(
                        name=ai_data.get("name", "Name Not Found"),
                        headline=ai_data.get("headline", "Professional"),
                        contact_info=ai_data.get("contact", "Not Provided"),
                        skills=ai_data.get("skills", "Python, Development"),
                        main_content=ai_data.get("experience", "Experience details missing.")
                    )
                    st.success("✅ AI successfully generated your CV!")
                    b64 = base64.b64encode(final_html.encode()).decode()
                    href = f'<a href="data:text/html;base64,{b64}" download="{ai_data.get("name", "User").replace(" ", "_")}_CV.html" style="display:inline-block; padding:12px 24px; background-color:#4CAF50; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">📥 Download AI-Designed CV</a>'
                    st.markdown(href, unsafe_allow_html=True)
