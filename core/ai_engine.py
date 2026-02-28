import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
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
    """Bulletproof JSON parser to prevent crashes."""
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return json.loads(response_text[start_idx:end_idx+1])
        return json.loads(response_text)
    except Exception as e:
        return {"name": "Parse Error", "headline": "Try again", "contact": "", "skills": "", "experience": "<p>Error parsing data.</p>", "education": "", "certificates": ""}

def extract_base_cv(raw_text):
    prompt = f"""
    You are an Expert ATS Resume Builder. Output ONLY STRICT JSON. Do not use markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".

    CRITICAL LOGIC BASED ON TEXT LENGTH:
    
    SCENARIO 1: DETAILED TEXT (PDF Resume Upload)
    - If the text is long and contains detailed history, extract EVERYTHING accurately.
    - Format beautifully using HTML <p>, <ul>, <li>. Do not hallucinate.

    SCENARIO 2: SHORT TEXT (URL Scrape / Fallback)
    - If the text is short (just Name, Headline, and a note):
    - DO NOT leave the CV empty. DO NOT write "Profile blocked".
    - DO NOT invent fake company names (No "XYZ Corp").
    - "headline": Use the provided headline/profession.
    - "skills": Generate 8-12 highly relevant industry skills based on the headline.
    - "experience": Write a strong professional summary paragraph. Then add a section like "<p><b>Core Expertise & Projects</b></p><ul><li>Successfully delivered projects and solutions in this domain.</li><li>Demonstrated strong analytical and technical abilities to drive results.</li></ul>". Keep it professional and factual to the industry.
    - "education": "<p><b>Academic Background</b></p><ul><li>Degree in relevant technical/business field</li></ul>"
    - "certificates": ""

    Text to process: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    return clean_and_parse_json(response_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System. Output ONLY STRICT JSON. No markdown blocks.
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Add missing keywords to skills. Rephrase experience to align with JD, but DO NOT ADD FAKE COMPANIES.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report".

    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    return clean_and_parse_json(response_text)
