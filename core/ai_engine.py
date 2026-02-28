import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.2, # Balanced temperature
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
        # Emergency fallback if AI goes completely crazy
        return {"name": "Data Processing Error", "headline": "Please try again.", "contact": "", "skills": "", "experience": "<p>Error parsing data.</p>", "education": "", "certificates": ""}

def extract_base_cv(raw_text):
    prompt = f"""
    You are an Expert ATS Resume Parser. Output ONLY STRICT JSON. Do not use markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".

    CRITICAL LOGIC BASED ON TEXT LENGTH:
    
    SCENARIO 1: DETAILED TEXT (e.g., PDF Resume Upload)
    If the text contains detailed history, jobs, and education:
    - Intelligently extract EVERYTHING. 
    - Fix messy formatting and organize it beautifully using HTML <p>, <ul>, <li> tags.
    - Do not leave any valid data behind.

    SCENARIO 2: SHORT TEXT (e.g., URL Scrape)
    If the text is very short (just Name, Title, and basic summary):
    - ZERO HALLUCINATION. Do NOT invent fake companies (like "XYZ Corp") or fake degrees.
    - Map the real title and summary into the "headline" and "experience" fields.
    - For completely missing sections (like education or certificates), return an EMPTY STRING "". Do not write "No data found".

    Text to process: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    return clean_and_parse_json(response_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System. Output ONLY STRICT JSON. No markdown blocks.
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Add missing keywords to skills. Rephrase experience to align with JD, but DO NOT ADD FAKE COMPANIES OR JOBS.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report".

    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    return clean_and_parse_json(response_text)
