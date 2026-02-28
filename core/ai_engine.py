import google.generativeai as genai
import json
import streamlit as st

def get_gemini_model():
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def extract_base_cv(raw_text):
    model = get_gemini_model()
    prompt = f"""
    Extract data into STRICT JSON. No markdown.
    Keys: "name", "headline", "contact", "skills" (comma separated), "experience" (format with basic HTML <p>, <ul>, <li>).
    If the text is sparse, intelligently expand the skills and experience based on the headline/name to make a complete profile.
    Text: {raw_text[:8000]}
    """
    response = model.generate_content(prompt)
    clean_text = response.text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    model = get_gemini_model()
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
    response = model.generate_content(prompt)
    clean_text = response.text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
