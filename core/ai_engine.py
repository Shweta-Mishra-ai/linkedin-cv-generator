import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.1, 
    )
    return response.choices[0].message.content

def generate_with_fallback(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        try:
            return call_groq(prompt)
        except Exception as groq_e:
            raise Exception(f"API Error: Both engines failed.")

def extract_base_cv(raw_text):
    prompt = f"""
    You are an expert Data Extractor. Extract the provided text into a STRICT JSON format. Do not use markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills", "experience", "education", "certificates".
    
    CRITICAL RULES - NO FAKE DATA:
    1. If the text contains "Name & Title" or "Headline & About", extract the real Name and Headline exactly as written.
    2. Read the "PAGE CONTENT" carefully. If you see ANY mention of jobs, roles, projects, degrees, or certifications, extract them into "experience" and "education".
    3. If "Headline & About" contains a long summary, include that summary at the top of the "experience" section.
    4. NEVER invent fake companies (like XYZ Corp) or generic terms.
    5. If a section (like Education or Certificates) is genuinely missing from the text, return exactly: "<p>Not available in public profile.</p>"
    6. Format all extracted data beautifully with HTML <p>, <ul>, <li>.
    
    Raw Scraped Text: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System and Resume Optimizer. Follow these steps sequentially:
    
    1. Evaluate the Base Resume against the JD to calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from the JD.
    3. Create "tailored_cv": Update skills with missing keywords. Rephrase experience slightly to highlight JD relevance ONLY using existing facts.
       CRITICAL: DO NOT ADD FAKE JOBS OR COMPANIES.
    4. Evaluate the new "tailored_cv" against the JD to calculate "new_ats_score" (0-100).
    5. Write an "analysis_report" explaining what you changed.
    
    Return STRICT JSON. No markdown blocks.
    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
