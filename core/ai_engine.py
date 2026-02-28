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
    gemini_error = None
    groq_error = None
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=temp))
        return response.text
    except Exception as e:
        gemini_error = str(e)
    try:
        return call_groq(prompt, temp)
    except Exception as groq_e:
        groq_error = str(groq_e)
    # Both failed - raise with real error details visible in logs
    raise Exception(f"API Error: Gemini failed [{gemini_error}], Groq failed [{groq_error}]")

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

def extract_base_cv(raw_text, is_url=False):
    if is_url:
        # For URLs: LinkedIn blocks most data, so we use AI to generate professional content
        prompt = f"""
You are an Expert Resume Architect. Output ONLY a raw JSON object. No markdown, no explanation.
Required keys: "name", "headline", "contact", "skills", "experience", "education", "certificates"

The text is a limited scrape from a LinkedIn URL (usually only name/headline is available due to login wall).
Your job: BUILD a complete professional CV based on whatever is in the text.

INSTRUCTIONS:
1. Extract the real name and headline from the text.
2. "skills": Generate 10-15 relevant skills as a comma-separated string based on the headline.
3. "experience": Generate 2-3 detailed, realistic job experiences as a SINGLE HTML string using <ul><li> tags. Match the profession. Use plausible company names (not "XYZ Corp").
4. "education": Generate a relevant degree as a SINGLE HTML string (e.g. "<p>B.Tech in Computer Science - IIT Delhi (2018)</p>").
5. "certificates": Generate 1-2 relevant industry certificates as a SINGLE HTML string.
6. "contact": Use "<p>LinkedIn Profile | India</p>" as placeholder.

Text: {raw_text[:4000]}
"""
    else:
        # For PDFs: extract all the real data from the detailed CV text
        prompt = f"""
You are an expert resume parser. Output ONLY a raw JSON object. No markdown, no explanation.
Required keys: "name", "headline", "contact", "skills", "experience", "education", "certificates"

INSTRUCTIONS:
1. Extract all available data from the text. Do not skip any information.
2. "skills": Extract all skills as a comma-separated string.
3. "experience": Format ALL work experience as a SINGLE HTML string using <p><b>Title at Company (Dates)</b></p><ul><li>Achievement</li></ul> structure.
4. "education": Format ALL education as a SINGLE HTML string using <p> tags.
5. "certificates": Format ALL certifications as a SINGLE HTML string using <p> tags.
6. "contact": Extract email, LinkedIn, phone, location as a single string.
7. If a section genuinely does not exist in the text, set it to "".

Text: {raw_text[:4000]}
"""
    response_text = generate_with_fallback(prompt, temp=0.3)
    return clean_and_parse_json(response_text, is_analysis=False)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    # Trim the CV JSON to avoid token limits on free API tiers
    trimmed_cv = json.dumps(base_cv_json)[:4000]
    prompt = f"""
Act as an Expert ATS System. Output ONLY a raw JSON object. No markdown, no explanation.
Required output keys: "old_ats_score", "missing_keywords", "tailored_cv", "new_ats_score", "analysis_report"

1. "old_ats_score": integer 0-100, how well the base CV matches the JD.
2. "missing_keywords": JSON array of 3-5 key terms from JD missing in CV.
3. "tailored_cv": JSON object with keys: name, headline, contact, skills, experience, education, certificates.
   - Copy name, headline, contact, education, certificates from base CV exactly.
   - Add missing keywords to skills (comma-separated string).
   - Rewrite experience as a single HTML string with <p><b>Title</b></p><ul><li> tags to align with JD.
4. "new_ats_score": integer 0-100, improved score after tailoring.
5. "analysis_report": JSON array of 3-5 short strings explaining changes made.

BASE CV: {trimmed_cv}
JD: {jd_text[:3000]}
"""
    response_text = generate_with_fallback(prompt, temp=0.2)
    return clean_and_parse_json(response_text, is_analysis=True)
