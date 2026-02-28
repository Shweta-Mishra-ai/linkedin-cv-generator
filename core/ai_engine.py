import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.0, # 🔴 ZERO CREATIVITY. STRICTLY REAL FACTS ONLY.
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
    You are a STRICT Data Extractor. Convert the text into STRICT JSON format. Do not use markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills" (comma string), "experience", "education", "certificates".

    CRITICAL RULES (READ CAREFULLY):
    1. ABSOLUTELY NO AI GENERATION: DO NOT write paragraphs praising the candidate. DO NOT invent ANY text.
    2. EXTRACT EXACT FACTS ONLY: If the text provides a "REAL HEADLINE/TITLE" or "REAL ABOUT/SUMMARY", copy that EXACT information into the "headline" and "experience" fields. Do not alter it.
    3. HIDE MISSING SECTIONS: If Education, Certificates, Experience, or Skills are NOT explicitly mentioned in the scraped text, return an EMPTY STRING "". 
       - DO NOT write "Data protected". 
       - DO NOT write "No data found". 
       - Just leave it completely empty ("") so the UI can hide the section cleanly.
    4. PDF TEXT: If it's a long PDF text, extract all facts normally into HTML <p>, <ul>, <li>.

    Text to process: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System.
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Add missing keywords to skills. DO NOT add fake companies or fake experience.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report".

    Return STRICT JSON. No markdown blocks.
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
