import google.generativeai as genai
import json
import streamlit as st

def generate_with_fallback(prompt):
    """
    SENIOR DEV TRICK: The Retry Cascade.
    Agar ek model Google ke server par fail hota hai, toh yeh code chupchap dusra model try karega
    bina user ko error dikhaye.
    """
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Hum saare latest models ki list bana lenge. Jo chalega, usse kaam nikal lenge.
    models_to_try = [
        'gemini-1.5-flash', 
        'gemini-1.5-flash-latest', 
        'gemini-1.0-pro', 
        'gemini-pro'
    ]
    
    last_error = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = e
            continue # Ek fail hua toh koi baat nahi, loop dusre model par chala jayega
            
    # Agar Google ka poora server hi down hai tabhi yeh error aayega
    raise Exception(f"Google API is currently unstable. Last error: {last_error}")

def extract_base_cv(raw_text):
    prompt = f"""
    Extract data into STRICT JSON. No markdown.
    Keys: "name", "headline", "contact", "skills" (comma separated), "experience" (format with basic HTML <p>, <ul>, <li>).
    If the text is sparse, intelligently expand the skills and experience based on the headline/name to make a complete profile.
    Text: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System. Compare Base Resume with JD.
    Tasks:
    1. Calculate old ATS score (0-100).
    2. Identify missing keywords.
    3. Calculate expected NEW ATS score (after tailoring).
    4. Create "tailored_cv" by naturally incorporating missing keywords into experience/skills. Do not lie.
    
    Return STRICT JSON. No markdown.
    Keys required:
    "old_ats_score": integer,
    "new_ats_score": integer,
    "missing_keywords": [list of strings],
    "improvements": [list of strings],
    "tailored_cv": {{"name": "...", "headline": "...", "contact": "...", "skills": "...", "experience": "..."}}
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
