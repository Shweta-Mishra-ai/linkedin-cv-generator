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
        print(f"Gemini API Error. Switching to Groq...")
        try:
            return call_groq(prompt)
        except Exception as groq_e:
            raise Exception(f"Both Engines failed. Groq Error: {str(groq_e)}")

def extract_base_cv(raw_text):
    prompt = f"""
    You are a strict data extractor for a hiring app. Read the text carefully.
    Extract the details into STRICT JSON format. Do not use markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".
    
    CRITICAL RULES:
    1. ZERO HALLUCINATION: DO NOT invent fake companies (like XYZ Corp) or fake degrees.
    2. USE PUBLIC META DATA: The text contains "PUBLIC META DATA". Use it! 
       - Extract the exact Name.
       - The 'Headline and Summary' usually contains their current job, location, and key roles. Put that in "headline" and "experience".
    3. If experience, education, or certificates are genuinely missing, return: "<p>Not available in public URL. Please upload PDF.</p>"
    4. Format valid data using HTML <p>, <ul>, <li>.
    
    Text: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System and Resume Optimizer. Follow these steps sequentially.
    
    Step 1. Evaluate the REAL Base Resume against the JD to calculate "old_ats_score".
    Step 2. Identify 3-5 crucial "missing_keywords" from the JD.
    Step 3. Create "tailored_cv": Update skills with missing keywords. Rephrase experience to highlight JD relevance. 
            CRITICAL RULE: DO NOT ADD FAKE JOBS, FAKE COMPANIES, OR FAKE DEGREES. Keep historical facts identical.
    Step 4. Evaluate the new "tailored_cv" against the JD to calculate "new_ats_score".
    Step 5. Write an "analysis_report" explaining what you changed to boost the score.
    
    Return STRICT JSON. No markdown blocks.
    Keys required:
    "old_ats_score": integer (0-100),
    "missing_keywords": [list of strings],
    "tailored_cv": {{"name": "...", "headline": "...", "contact": "...", "skills": "...", "experience": "...", "education": "...", "certificates": "..."}},
    "new_ats_score": integer (0-100),
    "analysis_report": [list of strings]
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
