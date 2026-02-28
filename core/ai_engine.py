import google.generativeai as genai
from groq import Groq
import json
import streamlit as st

def call_groq(prompt):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.0, 
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
    """Senior Dev Trick: Extracts ONLY the JSON part from AI output, ignoring extra text."""
    try:
        # Find the first '{' and the last '}'
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_string = response_text[start_idx:end_idx+1]
            return json.loads(json_string)
        else:
            # If brackets aren't found, try parsing the raw text anyway
            return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"CRITICAL PARSE ERROR. Raw Output was: {response_text}")
        raise e

def extract_base_cv(raw_text):
    prompt = f"""
    You are a STRICT Data Extractor. Convert the text into STRICT JSON format. 
    Keys required: "name", "headline", "contact", "skills" (comma string), "experience", "education", "certificates".

    CRITICAL RULES:
    1. EXTRACT EXACT FACTS ONLY: Copy the real headline and real summary into the respective fields.
    2. HIDE MISSING SECTIONS: If Education, Certificates, Experience, or Skills are NOT explicitly mentioned, return an EMPTY STRING "". Do NOT write "No data found".
    3. NO CHIT-CHAT: Output ONLY the JSON object. Do not say "Here is the data".
    
    Text to process: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    return clean_and_parse_json(response_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System.
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Add missing keywords to skills. DO NOT add fake companies or experience.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report".

    Return STRICT JSON. 
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    return clean_and_parse_json(response_text)
