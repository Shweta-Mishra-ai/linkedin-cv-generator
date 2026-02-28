def extract_base_cv(raw_text):
    prompt = f"""
    You are an expert data extractor. Extract the provided text into STRICT JSON. No markdown formatting or ```json blocks.
    Keys required: "name", "headline", "contact", "skills" (comma separated), "experience", "education", "certificates".
    
    CRITICAL RULES - READ CAREFULLY:
    1. ONLY extract information that is explicitly present in the provided text.
    2. DO NOT invent, guess, or hallucinate any fake data, fake companies (like "XYZ Corporation"), or fake degrees.
    3. If experience, education, or certificates are missing from the text, DO NOT make them up. Instead, return this exact string for that field: "<p><i>No data available. Please use the 'Upload PDF' method to bypass LinkedIn security.</i></p>"
    4. Format valid "experience", "education", and "certificates" with basic HTML <p>, <ul>, <li>.
    
    Text to extract: {raw_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)

def analyze_and_tailor_cv(base_cv_json, jd_text):
    prompt = f"""
    Act as an Expert ATS System. Compare the REAL Base Resume with the JD.
    Tasks:
    1. Calculate old ATS score (0-100) based strictly on current matching skills.
    2. Identify missing keywords from the JD.
    3. Calculate expected NEW ATS score.
    4. Provide an 'analysis_report' (list of 3-4 strings) explaining real gaps.
    5. Create "tailored_cv": You may add the missing keywords naturally into the skills section or slightly rephrase existing bullet points to match the JD vocabulary. DO NOT add fake jobs or fake companies.
    
    Return STRICT JSON. No markdown formatting or ```json blocks.
    Keys required:
    "old_ats_score": integer,
    "new_ats_score": integer,
    "missing_keywords": [list of strings],
    "analysis_report": [list of strings],
    "tailored_cv": {{"name": "...", "headline": "...", "contact": "...", "skills": "...", "experience": "...", "education": "...", "certificates": "..."}}
    
    BASE RESUME JSON: {json.dumps(base_cv_json)}
    JD: {jd_text[:8000]}
    """
    response_text = generate_with_fallback(prompt)
    clean_text = response_text.strip().removeprefix('```json').removeprefix('```').removesuffix('```').strip()
    return json.loads(clean_text)
