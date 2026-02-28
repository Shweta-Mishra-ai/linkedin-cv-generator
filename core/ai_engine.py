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
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=temp))
        return response.text
    except Exception as e:
        try:
            return call_groq(prompt, temp)
        except Exception as groq_e:
            raise Exception("API Error: Both engines failed.")

def clean_and_parse_json(response_text, is_analysis=False):
    """Bulletproof parser to fix the 'T, h, e' bug and UI crashes."""
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            parsed_data = json.loads(response_text[start_idx:end_idx+1])
        else:
            parsed_data = json.loads(response_text)
            
        if is_analysis:
            # 🛡️ THE ATS FIX: Forces analysis_report to be a proper List to stop single-letter printing
            report = parsed_data.get("analysis_report", ["Analysis complete."])
            if isinstance(report, str):
                parsed_data["analysis_report"] = [report]
            elif not isinstance(report, list):
                parsed_data["analysis_report"] = ["Analysis successfully generated."]
            return parsed_data
        else:
            # 🛡️ THE UI FIX: Ensures skills and other fields are always proper strings
            if isinstance(parsed_data.get("skills"), list):
                parsed_data["skills"] = ", ".join(str(x) for x in parsed_data["skills"])
            elif not parsed_data.get("skills"):
                parsed_data["skills"] = ""
                
            for key in ["experience", "education", "certificates"]:
                if parsed_data.get(key) is None:
                    parsed_data[key] = ""
                elif isinstance(parsed_data.get(key), list):
                    parsed_data[key] = "".join(str(x) for x in parsed_data[key])
            return parsed_data
    except Exception as e:
        if is_analysis:
            return {"old_ats_score": 0, "missing_keywords": [], "tailored_cv": {}, "new_ats_score": 0, "analysis_report": ["Analysis generation failed. Please try again."]}
        return {"name": "Candidate", "headline": "Professional", "contact": "", "skills": "", "experience": "Data extraction failed.", "education": "", "certificates": ""}

def extract_base_cv(raw_text):
    is_pdf = len(raw_text) > 1000

    if is_pdf:
        # PDF PROMPT: Untouched, keeps your PDF formatting perfect
        prompt = f"""
        You are an Expert Resume Parser. Output ONLY STRICT JSON.
        Keys required: "name", "headline", "contact", "skills" (comma separated string), "experience", "education", "certificates".

        CRITICAL RULES FOR PDF TEXT:
        1. Extract ALL details perfectly (jobs, education, projects).
        2. Format "experience", "education", and "certificates" beautifully using HTML <p>, <ul>, and <li> tags.
        
        Text to process: {raw_text[:8000]}
        """
        response_text = generate_with_fallback(prompt, temp=0.2)
    else:
        # 🌟 URL PROMPT: Builds a professional, non-empty, skill-based CV without fake companies
        prompt = f"""
        You are an Expert Resume Builder. Output ONLY STRICT JSON.
        Keys required: "name", "headline", "contact", "skills" (comma separated string), "experience", "education", "certificates".

        CRITICAL RULES FOR URL DATA:
        1. ZERO HALLUCINATION OF COMPANIES: DO NOT invent fake company names (like "XYZ Corp") or fake degrees.
        2. "name" & "headline": Extract from the text.
        3. "experience": Do NOT leave this empty. Write a professional 2-sentence overview based on their headline. Then, add a section called "<p><b>Core Expertise</b></p>" with 3 bullet points (<ul><li>) describing general industry skills for that profession. 
        4. "skills": Generate 8-10 highly relevant professional skills based on the headline.
        5. Leave "education" and "certificates" as EMPTY STRINGS "". DO NOT write "No data found".
        
        Text to process: {raw_text[:2000]}
        """
        response_text = generate_with_fallback(prompt, temp=0.2)

    return clean_and_parse_json(response_text, is_analysis=False)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System. Output ONLY STRICT JSON.
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Add missing keywords to skills ONLY.
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report" as an ARRAY OF STRINGS. Example: ["Keyword Python added.", "Optimized for Data role."]

    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report" (MUST BE A LIST OF STRINGS)
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt, temp=0.2)
    return clean_and_parse_json(response_text, is_analysis=True)
