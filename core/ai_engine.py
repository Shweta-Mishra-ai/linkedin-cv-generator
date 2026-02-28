import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.0, # STRICT ZERO HALLUCINATION
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
    """Bulletproof JSON parser to prevent crashes."""
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return json.loads(response_text[start_idx:end_idx+1])
        return json.loads(response_text)
    except Exception as e:
        return {"name": "Parse Error", "headline": "", "contact": "", "skills": "", "experience": "", "education": "", "certificates": ""}

def extract_base_cv(raw_text):
    prompt = f"""
    You are a STRICT Data Extractor. Output ONLY JSON. Do not write markdown blocks.
    Keys required: "name", "headline", "contact", "skills", "experience", "education", "certificates".

    CRITICAL RULES (FOLLOW EXACTLY):
    1. ZERO FAKE DATA: Extract exactly what is in the text. DO NOT invent companies, jobs, or paragraphs of text.
    2. If the text provides "REAL NAME AND TITLE" and "REAL SUMMARY", put the title in "headline" and the summary in "experience".
    3. MISSING SECTIONS: If a section (like education, skills, or certificates) is missing from the text, you MUST leave it as an empty string "". 
       - DO NOT write "Not available".
       - DO NOT write "No data found".
       - DO NOT write "Profile blocked".
       - Just return "" so the UI hides it cleanly.
    4. PDF TEXT: If detailed text is provided (e.g., from a PDF), extract all sections normally and accurately.

    Text: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    return clean_and_parse_json(response_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    # ATS Feature left 100% untouched and safe
    prompt = f"""
    Act as an Expert ATS System. Output ONLY STRICT JSON. No markdown blocks.
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Add missing keywords to skills ONLY.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report".

    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    return clean_and_parse_json(response_text)
