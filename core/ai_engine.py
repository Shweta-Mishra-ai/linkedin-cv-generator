import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt, temp=0.2):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=temp, 
    )
    return response.choices[0].message.content

def generate_with_fallback(prompt, temp=0.2):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Setting temperature dynamically based on PDF or URL
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=temp))
        return response.text
    except Exception as e:
        try:
            return call_groq(prompt, temp)
        except Exception as groq_e:
            raise Exception("API Error: Both engines failed.")

def clean_and_parse_json(response_text):
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return json.loads(response_text[start_idx:end_idx+1])
        return json.loads(response_text)
    except Exception as e:
        return {"name": "Data Error", "headline": "", "contact": "", "skills": "", "experience": "", "education": "", "certificates": ""}

def extract_base_cv(raw_text):
    # 🌟 THE ISOLATION LOGIC: Check if it's a PDF (>1000 chars) or URL (<1000 chars)
    is_pdf = len(raw_text) > 1000

    if is_pdf:
        # PATH A: PERFECT PDF PROMPT (Beautiful Formatting)
        prompt = f"""
        You are an Expert Resume Parser. Output ONLY STRICT JSON.
        Keys required: "name", "headline", "contact", "skills", "experience", "education", "certificates".

        CRITICAL RULES FOR PDF TEXT:
        1. Extract ALL details perfectly (jobs, education, projects).
        2. Format the "experience", "education", and "certificates" sections beautifully using HTML <p>, <ul>, and <li> tags for proper bullet points.
        3. Do not miss any valid data.
        
        Text to process: {raw_text[:8000]}
        """
        response_text = generate_with_fallback(prompt, temp=0.2)
    else:
        # PATH B: STRICT URL PROMPT (Zero Fake Data)
        prompt = f"""
        You are a STRICT Data Parser. Output ONLY STRICT JSON.
        Keys required: "name", "headline", "contact", "skills", "experience", "education", "certificates".

        CRITICAL RULES FOR URL DATA:
        1. ZERO HALLUCINATION: Extract EXACTLY what is provided. DO NOT invent fake companies, jobs, or skills.
        2. If you see "NAME AND TITLE", put it in "name" and "headline".
        3. If you see "SUMMARY", put it in "experience" wrapped in a <p> tag.
        4. Leave ALL missing sections ("skills", "education", "certificates", "contact") as completely EMPTY STRINGS "". DO NOT write "No data found".
        
        Text to process: {raw_text[:2000]}
        """
        response_text = generate_with_fallback(prompt, temp=0.0)

    return clean_and_parse_json(response_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System. Output ONLY STRICT JSON. No markdown blocks.
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Add missing keywords to skills. DO NOT add fake experience.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report".

    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt, temp=0.2)
    return clean_and_parse_json(response_text)
