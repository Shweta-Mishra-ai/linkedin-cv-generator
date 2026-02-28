import google.generativeai as genai
import json
import streamlit as st

def get_gemini_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # Auto-detect best model
        best_model = 'models/gemini-1.0-pro'
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name:
                    best_model = m.name
                    break
        return genai.GenerativeModel(best_model)
    except Exception as e:
        raise Exception("API Key missing or invalid.")

def extract_base_cv(raw_text):
    model = get_gemini_model()
    prompt = f"""
    Extract data from this profile text into STRICT JSON. No markdown.
    Keys: "name", "headline", "contact", "skills" (comma separated), "experience" (formatted with HTML <p>, <ul>, <li>).
    Text: {raw_text[:8000]}
    """
    response = model.generate_content(prompt)
    clean_text = response.text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    model = get_gemini_model()
    prompt = f"""
    Act as an Expert ATS System and Resume Writer. 
    Compare the Base Resume JSON with the Job Description (JD).
    
    Tasks:
    1. Calculate an ATS match score (0-100).
    2. Identify missing keywords from the JD.
    3. Create a "tailored_cv" by naturally incorporating the missing keywords and JD requirements into the skills and experience sections of the Base Resume. Do not lie, just rephrase and highlight relevant parts.
    
    Return STRICT JSON. No markdown.
    Keys required:
    "ats_score": integer,
    "missing_keywords": [list of strings],
    "improvements": [list of strings],
    "tailored_cv": {{"name": "...", "headline": "...", "contact": "...", "skills": "...", "experience": "..."}}
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JOB DESCRIPTION: {jd_text[:8000]}
    """
    response = model.generate_content(prompt)
    clean_text = response.text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
