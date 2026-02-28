import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    # Groq is SAFE and will be used for Fallback & Analysis
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.2, 
    )
    return response.choices[0].message.content

def generate_with_fallback(prompt):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        try:
            return call_groq(prompt)
        except Exception as groq_e:
            raise Exception("API Error: Both engines failed.")

def clean_and_parse_json(response_text):
    """Bulletproof JSON parser so app doesn't crash."""
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return json.loads(response_text[start_idx:end_idx+1])
        return json.loads(response_text)
    except Exception as e:
        return {"name": "Error", "headline": "", "contact": "", "skills": "", "experience": "", "education": "", "certificates": ""}

def extract_base_cv(raw_text):
    prompt = f"""
    You are a Data Extractor. Output ONLY JSON. 
    Keys: "name", "headline", "contact", "skills", "experience", "education", "certificates".

    SIMPLE MORNING RULES (NO FAKE DATA):
    1. Extract exactly what is in the text. DO NOT invent fake companies (like "XYZ Corp") or fake jobs.
    2. If you see "REAL NAME AND TITLE" and "REAL SUMMARY" from a URL, use them for the "name", "headline", and summarize it into "experience". 
    3. If any section (like education, certificates, or skills) is completely missing, DO NOT write "No data found". Leave it as an empty string "".
    4. If it's a long PDF text, extract all sections accurately and format with HTML <p>, <ul>, <li>.

    Text: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    return clean_and_parse_json(response_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    # ATS Analysis feature is SAFE and untouched
    prompt = f"""
    Act as an Expert ATS System. Output ONLY STRICT JSON. No markdown blocks.
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Add missing keywords to skills ONLY. Do NOT add fake companies.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report".

    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    return clean_and_parse_json(response_text)
