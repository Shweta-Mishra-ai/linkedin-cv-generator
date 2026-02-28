import google.generativeai as genai
import json
import time
import streamlit as st

def generate_with_fallback(prompt, retries=3):
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    valid_model = 'gemini-1.5-flash' # Default fallback
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for name in available_models:
            if 'flash' in name.lower():
                valid_model = name
                break
        if not valid_model and available_models:
            valid_model = available_models[0] 
    except:
        pass
        
    model = genai.GenerativeModel(valid_model)
    
    # SENIOR DEV TRICK: Auto-Retry for "ResourceExhausted" (Quota Limits)
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "resourceexhausted" in error_msg or "quota" in error_msg:
                if attempt < retries - 1:
                    time.sleep(5) # Wait 5 seconds to cool down API, then try again
                    continue
            raise e # If it's a different error, or out of retries, show it

def extract_base_cv(raw_text):
    prompt = f"""
    You are an expert resume builder. Extract data into STRICT JSON. No markdown.
    Keys: "name", "headline", "contact", "skills" (comma separated), "experience" (format with basic HTML <p>, <ul>, <li>).
    
    CRITICAL RULE: If the provided text is very short (under 100 words), it means the web scraper was blocked. In this case, YOU MUST ACT AS AN AI RESUME GENERATOR. 
    Use the name and headline to INVENT a completely realistic, highly professional, full-length resume. 
    - Write at least 3 detailed job experiences with 3 strong bullet points each.
    - Add at least 10-15 relevant industry skills.
    - Make it look like a highly experienced professional's CV.
    DO NOT RETURN A SHORT OR EMPTY CV.
    
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
    4. Provide an 'analysis_report' (list of 3-4 strings) explaining why the score improved.
    5. Create "tailored_cv" by naturally incorporating missing keywords into experience/skills. Do not lie, just rephrase.
    
    Return STRICT JSON. No markdown.
    Keys required:
    "old_ats_score": integer,
    "new_ats_score": integer,
    "missing_keywords": [list of strings],
    "analysis_report": [list of strings],
    "tailored_cv": {{"name": "...", "headline": "...", "contact": "...", "skills": "...", "experience": "..."}}
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
