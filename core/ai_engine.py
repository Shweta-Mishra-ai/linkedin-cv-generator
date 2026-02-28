import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    """Fallback Engine: Groq Llama 3.3 (Extremely Fast, Low Temperature to prevent fake data)"""
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile", # Latest working model
        temperature=0.1, # 🟢 LOW TEMP = NO HALLUCINATION / NO FAKE DATA
    )
    return response.choices[0].message.content

def generate_with_fallback(prompt):
    """Smart Fallback: Try Gemini 1.5. If it fails (Quota/Error), instantly use Groq."""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {str(e)}. Seamlessly switching to Groq...")
        try:
            return call_groq(prompt)
        except Exception as groq_e:
            raise Exception(f"Both AI Engines failed. Groq Error: {str(groq_e)}")

def extract_base_cv(raw_text):
    prompt = f"""
    You are a strict data extractor. Extract the provided text into STRICT JSON format. No markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".
    
    ZERO HALLUCINATION RULE: 
    - ONLY extract facts explicitly mentioned in the text. 
    - DO NOT invent, guess, or create fake companies, fake degrees, or fake skills. 
    - If experience, education, or certificates are missing, return exactly: "<p>No data found.</p>"
    - Format valid data using HTML <p>, <ul>, <li>.
    
    Text: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System and strict Resume Optimizer. Follow these exact logical steps sequentially.
    
    Step 1. Evaluate the REAL Base Resume against the Job Description (JD) to calculate the "old_ats_score".
    Step 2. Identify 3-5 crucial "missing_keywords" from the JD.
    Step 3. Create "tailored_cv": Update the skills list with missing keywords. Rephrase experience bullet points to highlight JD relevance. 
            CRITICAL ZERO-HALLUCINATION RULE: DO NOT ADD FAKE JOBS, FAKE COMPANIES (like XYZ Corp), OR FAKE DEGREES. Keep historical facts 100% identical.
    Step 4. Evaluate the newly created "tailored_cv" against the JD to calculate the "new_ats_score".
    Step 5. Write an "analysis_report" explaining exactly what you added/changed to boost the score.
    
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
