import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.1, 
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

def extract_base_cv(raw_text):
    prompt = f"""
    You are a Strict Data Extractor. Convert the provided text into STRICT JSON format. Do not use markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills", "experience", "education", "certificates".

    CRITICAL RULES FOR REAL DATA ONLY:
    1. ZERO FAKE DATA: DO NOT invent fake companies, DO NOT invent fake degrees, and DO NOT use generic filler like "Independent Consultant".
    2. SMART EXPERIENCE: If the text contains a "Summary" or "Description" from a public search profile, convert that summary into factual bullet points under "experience" (e.g., "<p><b>Professional Summary</b></p><ul><li>Skilled in AI and Data Science based on public profile data.</li></ul>"). Do not invent a company name if one isn't there.
    3. MISSING SECTIONS = EMPTY STRING: If education, skills, or certificates are NOT explicitly mentioned in the text, return an EMPTY STRING "". 
       - DO NOT write "No data found". 
       - DO NOT write "Not available".
       - Leave it completely blank "" so the UI hides the section cleanly.
    4. HTML FORMATTING: Use HTML <p>, <ul>, <li> for the text you do extract.

    Text to process: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System and Resume Optimizer. Follow these steps:
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Update skills with missing keywords. Enhance existing experience slightly to align with JD. DO NOT ADD FAKE COMPANIES.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report".

    Return STRICT JSON. No markdown blocks.
    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"

    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
