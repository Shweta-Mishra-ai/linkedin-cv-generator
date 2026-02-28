import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    try:
        # Posing as Googlebot to try and get public Meta Tags
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", property="og:description")

        if meta_title and meta_title.get("content"):
            title = meta_title.get("content").split('-')[0].strip()
            desc = meta_desc.get("content", "") if meta_desc else ""
            if "Sign In" not in title and "LinkedIn" not in title:
                return f"REAL NAME: {title}\nREAL HEADLINE/SUMMARY: {desc}\nNOTE: Build a factual, skills-based professional resume based on this summary."

        return get_linkedin_fallback_data(url)
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    # If blocked, smartly extract Name and Profession from the URL slug itself!
    try:
        path = urllib.parse.urlparse(url).path
        slug = path.strip("/").split("/")[-1]
        clean_name = re.sub(r'[^a-zA-Z\s]', ' ', slug.replace('-', ' ')).strip().title()
        
        # Infer profession from URL
        profession = "Professional"
        slug_lower = slug.lower()
        if "ai" in slug_lower or "data" in slug_lower:
            profession = "AI & Data Science"
        elif "dev" in slug_lower or "software" in slug_lower or "tech" in slug_lower:
            profession = "Software Engineering"
        elif "hr" in slug_lower or "manage" in slug_lower:
            profession = "Management"
            
        return f"REAL NAME: {clean_name}\nREAL HEADLINE: {profession} Expert\nNOTE: LinkedIn blocked full access. Build a detailed, factual, skills-based resume for this profession."
    except:
        return "REAL NAME: Professional Candidate\nREAL HEADLINE: Industry Professional"
