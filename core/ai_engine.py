import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.2, 
    )
    return response.choices[0].message.content

def generate_with_fallback(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini Limit Reached. Switching to Groq...")
        try:
            return call_groq(prompt)
        except Exception as groq_e:
            raise Exception(f"API Error. Groq Failed: {str(groq_e)}")

def extract_base_cv(raw_text):
    prompt = f"""
    You are an expert Resume Extraction & Generation AI.
    Convert the provided text into a STRICT JSON format. Do not use markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".
    
    CRITICAL RULES - READ CAREFULLY:
    1. NO FAKE COMPANIES: NEVER invent placeholder names like "XYZ Corporation" or "ABC Firm". 
    2. IF PDF TEXT (Detailed): Extract everything accurately. Do NOT ignore education, certificates, or experience. Format nicely with HTML <p>, <ul>, <li>.
    3. IF URL TEXT (Short Meta-data): Use the provided Name and Headline to INTELLIGENTLY BUILD a full, realistic professional CV. 
       - For Experience: Write skill-based achievements or use generic professional terms like "Independent Consultant", "Freelance Projects", or describe their skills practically.
       - For Education: Provide a realistic generic degree like "Relevant Degree in [Their Field]".
    4. NEVER output messages like "No data found", "Not available", or "Please upload PDF". ALWAYS provide a fully built-out CV structure.
    
    Text to process: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System and Resume Optimizer. Follow these steps sequentially:
    
    1. Evaluate the Base Resume against the JD to calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from the JD.
    3. Create "tailored_cv": Update skills with missing keywords. Rephrase experience to highlight JD relevance. 
       CRITICAL: DO NOT ADD FAKE JOBS like "XYZ Corp". Enhance the existing points intelligently.
    4. Evaluate the new "tailored_cv" against the JD to calculate "new_ats_score" (0-100).
    5. Write an "analysis_report" explaining what you changed to boost the score.
    
    Return STRICT JSON. No markdown blocks.
    Keys required:
    "old_ats_score": integer,
    "missing_keywords": [list of strings],
    "tailored_cv": {{"name": "...", "headline": "...", "contact": "...", "skills": "...", "experience": "...", "education": "...", "certificates": "..."}},
    "new_ats_score": integer,
    "analysis_report": [list of strings]
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
