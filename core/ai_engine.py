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

def extract_base_cv(raw_text):
    prompt = f"""
    You are an Expert ATS Resume Builder. Convert the text into STRICT JSON format. Do not use markdown blocks like ```json.
    Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".

    CRITICAL RULES:
    1. IF PDF DATA (Detailed text): Extract all real companies, jobs, and education perfectly.
    2. IF URL DATA (Sparse text with "Candidate Name"):
       - DO NOT leave the CV empty or write "No data found".
       - DO NOT invent fake companies like "XYZ Corp".
       - "headline": Write a strong professional title based on their name/page title.
       - "skills": Infer and list 8-10 highly relevant professional skills based on the context.
       - "experience": Write a 3-sentence "Professional Summary" praising their expertise in the field. Then add one bullet point: "<li><i>Detailed career history is protected by LinkedIn privacy settings. Please upload a PDF resume for full ATS analysis.</i></li>"
       - "education": "<p><i>Details protected by privacy settings.</i></p>"
       - "certificates": "" (Leave empty so the UI hides it).
    3. FORMATTING: Use HTML <p>, <ul>, <li>.

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
    3. Create "tailored_cv": Add missing keywords to skills. Do NOT add fake companies.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report".

    Return STRICT JSON. No markdown blocks.
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
