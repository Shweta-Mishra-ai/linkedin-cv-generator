import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    """Fallback function using Groq API"""
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192", # Fast and extremely smart model
        temperature=0.3,
    )
    return response.choices[0].message.content

def generate_with_fallback(prompt):
    """Tries Gemini first. If Quota Exceeded, seamlessly falls back to Groq."""
    try:
        # 1. First Priority: Gemini
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e).lower()
        # 2. Fallback: If Gemini hits limit (429/quota), switch to Groq!
        if "429" in error_msg or "quota" in error_msg or "resourceexhausted" in error_msg:
            print("Gemini limit reached. Switching to Groq...") # Logs for you
            try:
                return call_groq(prompt)
            except Exception as groq_e:
                raise Exception(f"Both AI engines failed. Groq Error: {str(groq_e)}")
        else:
            raise e # Raise if it's some other non-quota error

def extract_base_cv(raw_text):
    prompt = f"""
    You are an expert resume builder. Extract data into STRICT JSON. No markdown formatting or tags like ```json.
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
    5. Create "tailored_cv" by incorporating missing keywords.
    
    Return STRICT JSON. No markdown formatting.
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
