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

def _convert_to_html(value):
    """Converts any value type into a safe HTML string for rendering."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                # AI returned a list of dicts for experience - convert to HTML blocks
                lines = []
                for k, v in item.items():
                    lines.append(f"<b>{str(k).replace('_', ' ').title()}:</b> {str(v)}")
                parts.append("<div style='margin-bottom:15px;'>" + "<br>".join(lines) + "</div>")
            else:
                parts.append(f"<p>{str(item)}</p>")
        return "".join(parts)
    if isinstance(value, dict):
        # AI returned a single dict instead of a string
        lines = []
        for k, v in value.items():
            lines.append(f"<b>{str(k).replace('_', ' ').title()}:</b> {str(v)}")
        return "<div>" + "<br>".join(lines) + "</div>"
    return str(value)

def clean_and_parse_json(response_text, is_analysis=False):
    """Bulletproof JSON parser."""
    try:
        # Strip markdown code blocks if present
        clean = response_text.strip()
        if clean.startswith("```"):
            clean = clean[clean.find("{"):]  # strip ```json header
        if clean.endswith("```"):
            clean = clean[:clean.rfind("}") + 1]  # strip ``` footer

        start_idx = clean.find('{')
        end_idx = clean.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            parsed_data = json.loads(clean[start_idx:end_idx+1])
        else:
            parsed_data = json.loads(clean)

        if is_analysis:
            report = parsed_data.get("analysis_report", ["Analysis complete."])
            if isinstance(report, str):
                parsed_data["analysis_report"] = [report]
            elif not isinstance(report, list):
                parsed_data["analysis_report"] = ["Analysis generated."]
            # Also normalize tailored_cv if present
            tailored = parsed_data.get("tailored_cv", {})
            if isinstance(tailored, dict):
                for key in ["experience", "education", "certificates"]:
                    if key in tailored:
                        tailored[key] = _convert_to_html(tailored.get(key, ""))
                if isinstance(tailored.get("skills"), list):
                    tailored["skills"] = ", ".join(str(x) for x in tailored["skills"])
            return parsed_data
        else:
            # Normalize skills to comma-separated string
            if isinstance(parsed_data.get("skills"), list):
                parsed_data["skills"] = ", ".join(str(x) for x in parsed_data["skills"])
            elif not parsed_data.get("skills"):
                parsed_data["skills"] = ""

            # Normalize experience/education/certificates to HTML strings
            for key in ["experience", "education", "certificates"]:
                parsed_data[key] = _convert_to_html(parsed_data.get(key, ""))

            return parsed_data

    except Exception as e:
        if is_analysis:
            return {"old_ats_score": 0, "missing_keywords": [], "tailored_cv": {}, "new_ats_score": 0, "analysis_report": [f"Analysis failed: {str(e)}"]}
        return {"name": "Candidate", "headline": "Professional", "contact": "", "skills": "", "experience": f"<p>Data extraction error: {str(e)}</p>", "education": "", "certificates": ""}

def extract_base_cv(raw_text):
    prompt = f"""
    You are an expert resume builder. Extract the data from the text and output ONLY a single valid JSON object.
    Do NOT include markdown code blocks. Do NOT write any explanation. Just the raw JSON.
    Required keys: "name", "headline", "contact", "skills", "experience", "education", "certificates"

    RULES:
    1. "skills" must be a comma-separated string (e.g. "Python, SQL, Leadership").
    2. "experience", "education", "certificates" must each be a single HTML string using <p>, <ul>, <li> tags. Do NOT use nested JSON objects or arrays for these fields.
    3. Extract all available information from the text.
    4. If a section is missing, set it to an empty string "".

    Text: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt, temp=0.2)
    return clean_and_parse_json(response_text, is_analysis=False)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System. Output ONLY a single valid JSON object. No markdown blocks, no explanation.
    1. Calculate "old_ats_score" (0-100).
    2. Identify 3-5 "missing_keywords" as a JSON array of strings.
    3. Create "tailored_cv": A JSON object with these keys: "name", "headline", "contact", "skills", "experience", "education", "certificates".
       - Copy "name", "headline", "contact", "education", "certificates" directly from the base resume without changing them.
       - Improve "skills" by adding the missing keywords.
       - Improve "experience" HTML to better match the JD. Do NOT invent fake companies.
       - "experience", "education", "certificates" must be single HTML strings, not JSON arrays or objects.
    4. Calculate "new_ats_score" (0-100).
    5. Write "analysis_report" as a JSON array of strings.

    Keys required: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt, temp=0.2)
    return clean_and_parse_json(response_text, is_analysis=True)
