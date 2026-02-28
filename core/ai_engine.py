import google.generativeai as genai
import json
import streamlit as st

def generate_with_fallback(prompt):
    """
    ULTIMATE FIX: Hum koi naam hardcode nahi karenge. 
    Hum Google se available models ki list mangenge aur jo chalega use utha lenge.
    """
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    valid_model = None
    
    # 1. Google ke server se direct available models ki list nikalna
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            
    if not available_models:
        raise Exception("Aapki API key mein text generation available nahi hai. Shayad key block ho gayi hai.")
        
    # 2. Preference: Pehle 'flash' dhoondho (kyunki wo fast hai), warna jo pehla mile wo use kar lo
    for name in available_models:
        if 'flash' in name.lower():
            valid_model = name
            break
            
    if not valid_model:
        valid_model = available_models[0] # Jo bhi pehla working model mile
        
    # 3. Model run karna
    model = genai.GenerativeModel(valid_model)
    response = model.generate_content(prompt)
    return response.text

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
