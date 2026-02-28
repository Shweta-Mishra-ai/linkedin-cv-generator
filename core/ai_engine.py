import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    """Secondary API: Groq (Ultra-Fast Llama 3 Model)"""
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192", # Groq's smartest and fastest free model
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Groq API Error: {str(e)}")

def generate_with_fallback(prompt):
    """
    MASTER LOGIC: 
    1. Try Gemini first (Smart Model Picker).
    2. If Gemini throws ANY error (404, 429 Limit, etc.), instantly switch to Groq.
    """
    try:
        # Step 1: Attempt Gemini
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Smartly pick a model that exists on this specific API key to avoid 404
        valid_model = 'gemini-1.0-pro' 
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            for name in available_models:
                if '1.5-flash' in name:
                    valid_model = name
                    break
            # If 1.5-flash isn't available, pick anything that isn't the 20-limit model
            if valid_model not in available_models and available_models:
                for name in available_models:
                    if 'pro' in name or ('flash' in name and '2.5' not in name):
                        valid_model = name
                        break
        except:
            pass # Ignore list_models error and try fallback

        model = genai.GenerativeModel(valid_model)
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        # Step 2: Gemini Failed (Quota or 404). Activating Groq!
        print(f"Gemini Error ({str(e)}). Switching to Groq API...")
        return call_groq(prompt)

def extract_base_cv(raw_text):
    prompt = f"""
    You are an expert resume builder. Extract data into STRICT JSON. No markdown formatting or ```json blocks.
    Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".
    Format "experience", "education", and "certificates" with basic HTML <p>, <ul>, <li>.
    
    CRITICAL RULE: If the provided text is very short (under 100 words) or sparse, YOU MUST ACT AS AN AI RESUME GENERATOR. 
    Use the name and headline to INVENT a completely realistic, highly professional, full-length resume. 
    - Write at least 3 detailed job experiences.
    - Add at least 10-15 relevant skills.
    - Add a realistic Education section (e.g., Bachelor's Degree).
    - Add 1-2 realistic professional Certificates.
    
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
    3. Calculate expected NEW ATS score.
    4. Provide an 'analysis_report' (list of 3-4 strings) explaining why the score improved.
    5. Create "tailored_cv" by incorporating missing keywords naturally.
    
    Return STRICT JSON. No markdown formatting or ```json blocks.
    Keys required:
    "old_ats_score": integer,
    "new_ats_score": integer,
    "missing_keywords": [list of strings],
    "analysis_report": [list of strings],
    "tailored_cv": {{"name": "...", "headline": "...", "contact": "...", "skills": "...", "experience": "...", "education": "...", "certificates": "..."}}
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
