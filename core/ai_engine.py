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
    """Safe Parser (Untouched, keeps your app from crashing)"""
    try:
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            parsed_data = json.loads(response_text[start_idx:end_idx+1])
        else:
            parsed_data = json.loads(response_text)

        if is_analysis:
            report = parsed_data.get("analysis_report", ["Analysis complete."])
            if isinstance(report, str):
                parsed_data["analysis_report"] = [report]
            elif not isinstance(report, list):
                parsed_data["analysis_report"] = ["Analysis generated."]
            return parsed_data
        else:
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
            return {"old_ats_score": 0, "missing_keywords": [], "tailored_cv": {}, "new_ats_score": 0, "analysis_report": ["Analysis failed."]}
        return {"name": "Candidate", "headline": "Professional", "contact": "", "skills": "", "experience": "Data extraction failed.", "education": "", "certificates": ""}

def extract_base_cv(raw_text, is_url=False):
    if is_url:
        prompt = f"""
        You are an Expert ATS Resume Architect. Output ONLY STRICT JSON. Do not use markdown blocks like ```json.
        Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".

        The text provided is a limited scrape from a LinkedIn URL (usually just a Name and Title/Headline). 
        Your task is to BUILD A COMPLETE, PROFESSIONAL CV TEMPLATE based on this limited data.

        CRITICAL LOGIC FOR URL SCRAPE:
        1. Extract the actual Name and Headline from the text.
        2. "experience": INTELLIGENTLY GENERATE 2-3 realistic, highly professional job experiences that perfectly match the person's Headline. Add detailed, bulleted accomplishments using HTML <ul> and <li> tags. Do not use generic names like "XYZ Corp", use plausible placeholder names like "Tech Innovators Inc." or just refer to the role.
        3. "skills": Generate a comma-separated list of 10-15 highly relevant industry skills based on the Headline.
        4. "education": Generate a realistic, relevant college degree placeholder (e.g., "B.S. in Computer Science - University Name"). Use HTML tags if needed.
        5. "certificates": Generate 1-2 realistic industry-standard certificate placeholders matching the profession.
        6. "contact": Add a placeholder like "linkedin.com/in/profile | city, state".

        Make the generated content sound extremely professional and tailored to whatever title/headline is provided.
        
        Text to process: {raw_text[:8000]}
        """
    else:
        prompt = f"""
        You are an Expert ATS Resume Parser. Output ONLY STRICT JSON. Do not use markdown blocks like ```json.
        Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".

        CRITICAL LOGIC BASED ON TEXT LENGTH:
        
        SCENARIO 1: DETAILED TEXT (e.g., PDF Resume Upload)
        If the text contains detailed history, jobs, and education:
        - Intelligently extract EVERYTHING. 
        - Fix messy formatting and organize it beautifully using HTML <p>, <ul>, <li> tags.
        - Do not leave any valid data behind.

        SCENARIO 2: SHORT TEXT
        If the text is very short (just Name, Title, and basic summary):
        - ZERO HALLUCINATION. Do NOT invent fake companies (like "XYZ Corp") or fake degrees.
        - Map the real title and summary into the "headline" and "experience" fields.
        - For completely missing sections (like education or certificates), return an EMPTY STRING "". Do not write "No data found".

        Text to process: {raw_text[:8000]}
        """
    response_text = generate_with_fallback(prompt, temp=0.2)
    return clean_and_parse_json(response_text, is_analysis=False)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System. Output ONLY STRICT JSON.
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" from JD.
    3. Create "tailored_cv": Add missing keywords to skills. Rephrase experience to align with JD, but DO NOT ADD FAKE COMPANIES OR JOBS.
    **CRITICAL**: The "tailored_cv" JSON object MUST contain ALL original keys from the base resume: "name", "headline", "contact", "education", "certificates". Do not lose the candidate's name or other factual info!
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report" as an ARRAY OF STRINGS (e.g., ["Added Python.", "Improved format."]).

    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt, temp=0.2)
    return clean_and_parse_json(response_text, is_analysis=True)
