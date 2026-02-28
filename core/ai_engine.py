import google.generativeai as genai
import json
import streamlit as st

def call_gemini(prompt):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Strictly using the stable 1.5-flash model
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def extract_base_cv(raw_text):
    prompt = f"""
    You are a strict data extractor. Extract the provided text into STRICT JSON format. Do not use markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".
    
    ZERO HALLUCINATION RULE: 
    - ONLY extract facts explicitly mentioned in the text. 
    - DO NOT invent, guess, or create fake companies, fake degrees, or fake skills. 
    - If experience, education, or certificates are missing from the text, return exactly: "<p>No data found.</p>"
    - Format valid data using HTML <p>, <ul>, <li>.
    
    Text: {raw_text[:8000]}
    """
    response_text = call_gemini(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System. Compare the REAL Base Resume with the JD.
    Tasks:
    1. "old_ats_score": Calculate an honest score (0-100) based strictly on current matching skills.
    2. "missing_keywords": List 3-5 keywords from the JD that are missing.
    3. "new_ats_score": Calculate expected NEW ATS score.
    4. "analysis_report": A list of 3 strings explaining what was optimized.
    5. "tailored_cv": Update the skills list with the missing keywords. You may slightly rephrase experience bullet points to match the JD context, but YOU MUST NOT ADD FAKE JOBS, FAKE COMPANIES, OR FAKE DEGREES. Keep the core facts identical.
    
    Return STRICT JSON. No markdown blocks.
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = call_gemini(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
