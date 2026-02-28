import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.2, # Balanced creativity to format CV nicely without hallucinating
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
            raise Exception("API Error: Both Gemini and Groq engines failed.")

def extract_base_cv(raw_text):
    prompt = f"""
    You are an expert Resume Data Extractor. Convert the provided text into a STRICT JSON format.
    Do NOT use markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".

    CRITICAL RULES - READ CAREFULLY:
    1. NO FAKE DATA: NEVER invent fake companies (like "XYZ Corp"), fake jobs ("Independent Consultant"), or fake degrees.
    2. MAXIMIZE SHORT URL DATA: If the text only has a Name and a Headline/Summary:
       - Extract ALL professional keywords from the headline into the "skills" string.
       - Use the headline/summary to create a FACTUAL "experience" entry. (e.g., If headline says "Data Analyst", write an experience bullet: "<p><b>Data Professional</b></p><ul><li>Focused on Data Analysis and related technologies based on public profile summary.</li></ul>"). Do not leave experience empty if there is a headline.
    3. LONG PDF TEXT: Extract everything perfectly into the correct keys.
    4. MISSING DATA (VERY IMPORTANT): If education or certificates are completely missing, return an EMPTY STRING "". Do NOT write "No data found" or "Not available". This allows the UI to hide those sections cleanly.
    5. FORMATTING: Use HTML <p>, <ul>, <li> for experience, education, and certificates.

    Text to process: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System and Resume Optimizer. Follow these steps:
    1. Calculate "old_ats_score" (0-100) comparing Base Resume to JD.
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Update skills with missing keywords. Rephrase existing experience slightly to align with JD, but DO NOT ADD FAKE JOBS OR COMPANIES.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report" explaining the changes.

    Return STRICT JSON. No markdown blocks.
    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"

    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
