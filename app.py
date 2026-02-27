import streamlit as st
import PyPDF2
import google.generativeai as genai
import json
import base64

st.set_page_config(page_title="AI Pro CV Generator", page_icon="✨", layout="wide")

# --- SIDEBAR FOR API KEY ---
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("Get your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)")
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

st.title("✨ AI-Powered LinkedIn to CV Generator")
st.markdown("Upload any LinkedIn PDF. Our AI will read it, extract the exact details, and design a beautiful CV.")

# --- CSS/HTML TEMPLATE ---
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

# --- AI EXTRACTION LOGIC ---
def extract_data_with_ai(raw_text):
    genai.configure(api_key=api_key)
    # Using gemini-1.5-flash as it is fast and free
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert HR recruiter. Analyze the following LinkedIn profile text and extract the information into a STRICT JSON format. 
    Do not add any markdown formatting like ```json or ``` to the output. Return ONLY the raw JSON object.
    
    Use these exact keys:
    - "name": The person's full name.
    - "headline": Their current job title or main headline.
    - "contact": Their email or location (if not found, write "Contact info not public").
    - "skills": A comma-separated list of their top 5-8 skills.
    - "experience": A well-formatted summary of their experience, projects, and education. Use basic HTML tags like <p>, <ul>, <li>, and <strong> to make it look beautiful and easy to read.

    Here is the LinkedIn Profile Text:
    {raw_text}
    """
    
    response = model.generate_content(prompt)
    
    try:
        # Clean the response in case the AI adds markdown code blocks
        clean_text = response.text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
        data = json.loads(clean_text)
        return data
    except Exception as e:
        return None

# ---------------------------------------------------------
# APP LOGIC
# ---------------------------------------------------------
st.info("Upload any LinkedIn Profile PDF. The AI will intelligently read the data and structure it.")
uploaded_file = st.file_uploader("Upload PDF File", type=['pdf'])

if uploaded_file is not None:
    if not api_key:
        st.warning("⚠️ Please enter your Gemini API Key in the sidebar to continue.")
    else:
        if st.button("Generate AI Pro CV", type="primary"):
            with st.spinner("AI is reading the profile and designing the CV..."):
                # 1. Read PDF
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                raw_text = ""
                for page in pdf_reader.pages:
                    raw_text += page.extract_text() + "\n"
                
                # 2. Send to AI
                ai_data = extract_data_with_ai(raw_text)
                
                if ai_data:
                    # 3. Generate HTML using AI data
                    final_html = generate_html_cv(
                        name=ai_data.get("name", "Name Not Found"),
                        headline=ai_data.get("headline", "Professional Headline"),
                        contact_info=ai_data.get("contact", "Not Provided"),
                        skills=ai_data.get("skills", "Communication, Leadership"),
                        main_content=ai_data.get("experience", "Experience details not found.")
                    )
                    
                    st.success(f"✅ AI successfully generated the CV for {ai_data.get('name')}!")
                    
                    # 4. Download Button
                    b64 = base64.b64encode(final_html.encode()).decode()
                    href = f'<a href="data:text/html;base64,{b64}" download="{ai_data.get("name", "User").replace(" ", "_")}_AI_CV.html" style="display:inline-block; padding:12px 24px; background-color:#4CAF50; color:white; text-decoration:none; border-radius:5px; font-weight:bold;">📥 Download AI-Designed CV</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.caption("Open the downloaded file in your browser and press Ctrl+P to save it as a PDF.")
                else:
                    st.error("❌ AI failed to parse the document. Please try again.")
