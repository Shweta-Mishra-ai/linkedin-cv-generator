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
                    html_parts = []
                    for item in parsed_data[key]:
                        if isinstance(item, dict):
                            # Convert dict keys into basic HTML if the AI hallucinated an object
                            html_parts.append("<div style='margin-bottom:15px;'>" + "<br>".join([f"<b>{str(k).title()}:</b> {str(v)}" for k, v in item.items()]) + "</div>")
                        else:
                            html_parts.append(f"<p>{str(item)}</p>")
                    parsed_data[key] = "".join(html_parts)
            return parsed_data
    except Exception as e:
        if is_analysis:
            return {"old_ats_score": 0, "missing_keywords": [], "tailored_cv": {}, "new_ats_score": 0, "analysis_report": ["Analysis failed."]}
        return {"name": "Candidate", "headline": "Professional", "contact": "", "skills": "", "experience": "Data extraction failed.", "education": "", "certificates": ""}

def extract_base_cv(raw_text):
    prompt = f"""
    You are an expert resume builder. Extract the data from the text into STRICT JSON format.
    Keys required: "name", "headline", "contact", "skills" (comma separated string), "experience", "education", "certificates".

    RULES:
    1. Extract whatever information is available in the text.
    2. Do NOT invent fake companies like "XYZ Corp". Use generic professional terms if needed based on their headline/summary.
    3. The values for "experience", "education", and "certificates" MUST BE A SINGLE MULTI-LINE STRING containing beautiful HTML <p>, <ul>, and <li> tags. Do NOT output arrays or nested JSON objects for these fields.
    4. If a section is missing (e.g. from limited URL scraping), intelligently infer realistic professional placeholders based on their headline so the CV template renders fully and beautifully.

    Text: {raw_text[:8000]}
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
    **CRITICAL 2**: The values for "experience", "education", and "certificates" inside "tailored_cv" MUST BE A SINGLE HTML STRING (using <p>, <ul>, <li>). Do NOT output arrays or objects!
    4. Calculate "new_ats_score" (0-100).
    5. Write an "analysis_report" as an ARRAY OF STRINGS (e.g., ["Added Python.", "Improved format."]).

    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt, temp=0.2)
    return clean_and_parse_json(response_text, is_analysis=True)
