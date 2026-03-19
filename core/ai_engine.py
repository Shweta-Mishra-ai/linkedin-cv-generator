import google.generativeai as genai
from groq import Groq
import json
import re
import streamlit as st

# ────────────────────────────────────────────
# API CALL HELPERS
# ────────────────────────────────────────────

def call_groq(prompt, temp=0.2):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=temp,
        max_tokens=4096,
    )
    return response.choices[0].message.content

def generate_with_fallback(prompt, temp=0.2):
    gemini_error = None
    groq_error = None

    gemini_models = ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        for model_name in gemini_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(temperature=temp, max_output_tokens=4096)
                )
                return response.text
            except Exception as model_err:
                if "404" in str(model_err) or "not found" in str(model_err).lower():
                    continue
                raise model_err
        gemini_error = "No supported Gemini model found"
    except Exception as e:
        gemini_error = str(e)

    try:
        return call_groq(prompt, temp)
    except Exception as groq_e:
        groq_error = str(groq_e)

    raise Exception(f"API Error: Gemini failed [{gemini_error}], Groq failed [{groq_error}]")


# ────────────────────────────────────────────
# JSON PARSING & NORMALISATION
# ────────────────────────────────────────────

def _to_html(value):
    """Convert any AI output (str/list/dict) into a safe HTML string."""
    if value is None or value == "" or value == []:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict):
                title = item.get("title", item.get("role", item.get("position", item.get("company", ""))))
                company = item.get("company", item.get("organization", ""))
                dates = item.get("dates", item.get("duration", item.get("period", "")))
                bullets = item.get("bullets", item.get("responsibilities", item.get("achievements", item.get("description", []))))
                
                header = " at ".join(filter(None, [title, company]))
                if dates:
                    header += f" ({dates})"
                
                html = f"<p><b>{header}</b></p>" if header else ""
                if isinstance(bullets, list):
                    html += "<ul>" + "".join(f"<li>{b}</li>" for b in bullets if b) + "</ul>"
                elif isinstance(bullets, str) and bullets:
                    html += f"<ul><li>{bullets}</li></ul>"
                else:
                    # Fallback: render each key-value pair
                    for k, v in item.items():
                        if k not in ["title","role","position","company","organization","dates","duration","period"]:
                            html += f"<p><b>{str(k).replace('_',' ').title()}:</b> {str(v)}</p>"
                parts.append(html)
            else:
                parts.append(f"<p>{str(item)}</p>")
        return "".join(parts)
    if isinstance(value, dict):
        lines = [f"<b>{str(k).replace('_',' ').title()}:</b> {str(v)}" for k, v in value.items()]
        return "<div>" + "<br>".join(lines) + "</div>"
    return str(value)


def _extract_json(text):
    """Robustly extract JSON from AI response."""
    if not text:
        return None
    clean = text.strip()
    # Strip markdown code fences
    clean = re.sub(r'^```(?:json)?\s*', '', clean)
    clean = re.sub(r'\s*```$', '', clean)
    
    # Find outermost {...}
    start = clean.find('{')
    end = clean.rfind('}')
    if start != -1 and end != -1 and end > start:
        return clean[start:end+1]
    return clean


def clean_and_parse_json(response_text, is_analysis=False):
    """Bulletproof parser with rich fallback."""
    try:
        json_str = _extract_json(response_text or "")
        if not json_str:
            raise ValueError("Empty response")
        parsed = json.loads(json_str)

        if is_analysis:
            # Ensure all required keys exist
            parsed.setdefault("old_ats_score", 0)
            parsed.setdefault("new_ats_score", 0)
            parsed.setdefault("missing_keywords", [])
            parsed.setdefault("formatting_issues", [])
            parsed.setdefault("keyword_match_details", "Analysis complete.")
            parsed.setdefault("hallucination_check", "Safe. All data grounded in original CV.")
            parsed.setdefault("analysis_report", ["Analysis complete."])
            parsed.setdefault("improvements_made", [])

            # Fix types
            if isinstance(parsed.get("analysis_report"), str):
                parsed["analysis_report"] = [parsed["analysis_report"]]
            if isinstance(parsed.get("missing_keywords"), str):
                parsed["missing_keywords"] = [kw.strip() for kw in parsed["missing_keywords"].split(",")]

            # Normalise tailored_cv inner fields
            tailored = parsed.get("tailored_cv", {})
            if isinstance(tailored, dict):
                for key in ["experience", "education", "certificates", "projects"]:
                    if key in tailored:
                        tailored[key] = _to_html(tailored[key])
                if isinstance(tailored.get("skills"), list):
                    tailored["skills"] = ", ".join(str(x) for x in tailored["skills"])
            return parsed

        else:
            # Normalise base CV fields
            if isinstance(parsed.get("skills"), list):
                parsed["skills"] = ", ".join(str(x) for x in parsed["skills"])
            elif not parsed.get("skills"):
                parsed["skills"] = ""

            for key in ["experience", "education", "certificates", "projects"]:
                parsed[key] = _to_html(parsed.get(key, ""))

            # Ensure all required keys exist
            parsed.setdefault("name", "Candidate")
            parsed.setdefault("headline", "Professional")
            parsed.setdefault("contact", "")
            parsed.setdefault("summary", "")
            return parsed

    except Exception as e:
        if is_analysis:
            return {
                "old_ats_score": 0, "new_ats_score": 0,
                "missing_keywords": [], "formatting_issues": [],
                "keyword_match_details": f"Parse error: {e}",
                "hallucination_check": "Unknown",
                "tailored_cv": {}, "analysis_report": [f"Analysis failed: {e}"],
                "improvements_made": []
            }
        return {
            "name": "Candidate", "headline": "Professional",
            "contact": "", "skills": "", "summary": "",
            "experience": f"<p><b>Error:</b> {e}. Please try again.</p>",
            "projects": "", "education": "", "certificates": ""
        }


# ────────────────────────────────────────────
# CORE FUNCTION 1: EXTRACT BASE CV
# ────────────────────────────────────────────

EXTRACT_PROMPT = """
You are a world-class professional CV writer and data extractor.
Your job: parse the input text and extract a complete, structured CV as a JSON object.

OUTPUT: ONLY a raw JSON object. No markdown code fences. No explanation.

Required JSON keys:
- "name": Full name of the candidate (string)
- "headline": Professional title / tagline (string, max 2 lines)
- "summary": A 2-3 sentence professional summary of the candidate (write one if not present)
- "contact": Pipe-separated contact details e.g. "email@email.com | +91-9999 | linkedin.com/in/user | City, Country | github.com/user"
- "skills": Comma-separated technical and soft skills (string)
- "experience": SINGLE HTML string. Each job uses this format EXACTLY:
    <p><b>Job Title at Company Name (Start – End)</b></p>
    <ul><li>Achievement or responsibility bullet</li><li>...</li></ul>
  Write RICH, quantified bullets. If numbers/metrics exist, include them. Min 2 bullets per role.
- "projects": SINGLE HTML string. Each project uses:
    <p><b>Project Name | Technology Stack</b></p>
    <ul><li>What was built, impact, key achievement</li></ul>
  Leave "" if no projects exist.
- "education": SINGLE HTML string using <p> tags. Format: <p><b>Degree, Institution</b><br>Year | CGPA/Marks (if present)</p>
- "certificates": SINGLE HTML string using <p> tags. Each: <p><b>Cert Name</b> — Issuer (Year)</p>

RULES:
- DO NOT INVENT DATA. Extract only what's in the text.
- If a field is genuinely absent, set it to empty string "".
- Write experience bullets in STAR format (Situation, Task, Action, Result) where possible.
- Make the summary and headline professional and impactful.

TEXT TO PARSE:
{text}
"""

def extract_base_cv(raw_text, is_url=False):
    if is_url:
        prompt = EXTRACT_PROMPT.replace("{text}", raw_text[:14000]) + "\n\nNote: This text is from a web scrape. Extract whatever is available and write a strong professional summary."
    else:
        prompt = EXTRACT_PROMPT.replace("{text}", raw_text[:14000])
    
    response_text = generate_with_fallback(prompt, temp=0.15)
    return clean_and_parse_json(response_text, is_analysis=False)


# ────────────────────────────────────────────
# CORE FUNCTION 2: ATS ANALYSIS + TAILOR
# ────────────────────────────────────────────

ATS_PROMPT = """
You are a Senior ATS (Applicant Tracking System) Expert and Professional CV Coach.
Perform a deep analysis of the candidate's CV against the Job Description.

OUTPUT: ONLY a raw JSON object. No markdown. No explanation. No extra text.

Required JSON keys:

1. "old_ats_score": integer 0-100 — Current match score of CV vs JD. Be precise and honest.
2. "new_ats_score": integer 0-100 — Predicted score after your tailoring.
3. "missing_keywords": JSON array of 5-8 important JD keywords/phrases ABSENT from the CV.
4. "keyword_match_details": string — Detailed explanation of what keywords matched, which didn't, and why the score is what it is.
5. "formatting_issues": JSON array of 2-4 specific structural issues in the base CV (e.g., "Missing professional summary", "No quantified achievements", "Education section unclear").
6. "section_scores": JSON object with scores (0-100) for each section: {{"experience": 0, "skills": 0, "education": 0, "projects": 0, "overall_format": 0}}
7. "improvements_made": JSON array of 5-8 specific, concrete improvements made in the tailored CV (e.g., "Added 'Machine Learning' keyword to Data Analyst bullet point", "Rewrote summary to target Fintech industry").
8. "hallucination_check": string — Must say "Safe" if you added NO fake data. Describe any compromises.
9. "analysis_report": JSON array of 4-6 strategic insights about what the candidate should focus on for this application.
10. "tailored_cv": JSON object — The improved CV with the same structure as the base CV:
    {{
      "name": "...", "headline": "...", "summary": "...", "contact": "...",
      "skills": "...",  (reorder to put JD-relevant skills first)
      "experience": "...",  (rewrite bullets to highlight JD keywords — NO fake jobs)
      "projects": "...",  (rewrite to highlight JD-relevant tech — NO fake projects)
      "education": "...",
      "certificates": "..."
    }}
    
    CRITICAL RULES FOR tailored_cv:
    - FORBIDDEN: Adding fake job titles, fake companies, fake degrees, fake durations, fake projects
    - ALLOWED: Reordering skills, rewriting bullet language to use JD keywords, adding a targeted summary
    - Format experience/projects as HTML with <p><b>Title at Company (Dates)</b></p><ul><li>bullet</li></ul>

BASE CV:
{cv}

JOB DESCRIPTION:
{jd}
"""

def analyze_and_tailor_cv(base_cv_json, jd_text):
    cv_str = json.dumps(base_cv_json, ensure_ascii=False)[:12000]
    prompt = ATS_PROMPT.replace("{cv}", cv_str).replace("{jd}", jd_text[:8000])
    response_text = generate_with_fallback(prompt, temp=0.15)
    return clean_and_parse_json(response_text, is_analysis=True)
