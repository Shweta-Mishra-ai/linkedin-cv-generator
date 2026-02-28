import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import streamlit as st
import json

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    """
    Attempts to fetch REAL LinkedIn profile data using the RapidAPI "Fresh LinkedIn Profile Data" API.
    If no API key is set, or if the API call fails, it falls back to basic public scraping.
    """
    rapidapi_key = st.secrets.get("RAPIDAPI_KEY", None)

    if rapidapi_key:
        api_endpoint = "https://fresh-linkedin-profile-data.p.rapidapi.com/enrich-lead"
        querystring = {"linkedin_url": url, "include_skills": "true"}
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "fresh-linkedin-profile-data.p.rapidapi.com"
        }
        
        try:
            response = requests.get(api_endpoint, headers=headers, params=querystring, timeout=15)
            if response.status_code == 200:
                data = response.json()
                # Some APIs nest data inside 'data' key
                if 'data' in data and isinstance(data['data'], dict):
                    profile = data['data']
                else:
                    profile = data
                
                # Compose text document representing the profile
                real_data = []
                real_data.append(f"REAL NAME: {profile.get('full_name', '') or profile.get('firstName', '') + ' ' + profile.get('lastName', '')}")
                real_data.append(f"REAL HEADLINE/TITLE: {profile.get('headline', '')}")
                real_data.append(f"REAL ABOUT/SUMMARY: {profile.get('summary', '') or profile.get('about', '')}")
                loc = profile.get('location', {})
                if isinstance(loc, dict):
                    real_data.append(f"LOCATION: {loc.get('default', '') or loc.get('country', '')}")
                elif isinstance(loc, str):
                    real_data.append(f"LOCATION: {loc}")
                
                # Experiences
                real_data.append("\n--- EXPERIENCE ---")
                experiences = profile.get('experiences', []) or profile.get('experience', []) or []
                for exp in experiences:
                    real_data.append(f"Role: {exp.get('title') or exp.get('jobTitle')}")
                    real_data.append(f"Company: {exp.get('company') or exp.get('companyName')}")
                    real_data.append(f"Description: {exp.get('description', '')}")
                    real_data.append("-")
                
                # Education
                real_data.append("\n--- EDUCATION ---")
                education = profile.get('education', []) or profile.get('educations', []) or []
                for edu in education:
                    real_data.append(f"Degree: {edu.get('degree_name') or edu.get('degree')}")
                    real_data.append(f"School: {edu.get('school') or edu.get('schoolName')}")
                    real_data.append("-")
                
                # Skills
                real_data.append("\n--- SKILLS ---")
                skills = profile.get('skills', []) or []
                if skills and isinstance(skills, list):
                    # Handle if skills are dicts vs strings
                    if len(skills) > 0 and isinstance(skills[0], dict):
                        skills = [s.get('name', '') for s in skills]
                    real_data.append(", ".join([s for s in skills if isinstance(s, str)]))
                
                # Certifications
                real_data.append("\n--- CERTIFICATIONS ---")
                certs = profile.get('certifications', []) or profile.get('licenses_and_certifications', []) or []
                for cert in certs:
                    real_data.append(f"Name: {cert.get('name')} from {cert.get('authority') or cert.get('company')}")
                
                return "\n".join(real_data)
        except Exception as e:
            st.error(f"RapidAPI failed: {e}. Falling back to basic scrape.")
            # Fallback deliberately passes to the logic below

    # --- FALLBACK: Basic Public Scrape ---
    try:
        # Original simple request from the morning
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", property="og:description")

        data = ""
        if meta_title:
            data += f"Name/Title: {meta_title.get('content')}\n"
        if meta_desc:
            data += f"Summary: {meta_desc.get('content')}\n"

        # Also grabbing whatever body text is available like we did originally
        for script in soup(["script", "style"]):
            script.decompose()
        page_text = soup.get_text(separator=' ', strip=True)

        return data + "\n" + page_text[:3000]
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    try:
        path = urllib.parse.urlparse(url).path
        slug = path.strip("/").split("/")[-1]
        clean_name = re.sub(r'[^a-zA-Z\s]', ' ', slug.replace('-', ' ')).strip().title()
        return f"REAL NAME: {clean_name}\nNOTE: Full profile blocked by LinkedIn login wall. Using limited title data."
    except:
        return "Name: Candidate"
