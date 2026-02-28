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
        # Standard request
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find("title").text if soup.find("title") else ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        desc = meta_desc.get("content", "") if meta_desc else ""

        # Smart URL parsing (Foolproof way to get Name)
        path = urllib.parse.urlparse(url).path
        slug = path.strip("/").split("/")[-1]
        clean_name = re.sub(r'[^a-zA-Z\s]', ' ', slug.replace('-', ' ')).strip().title()

        return f"Candidate Name: {clean_name}\nPage Title: {title}\nSummary: {desc}\nNote: Full data restricted by LinkedIn."
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    try:
        path = urllib.parse.urlparse(url).path
        slug = path.strip("/").split("/")[-1]
        clean_name = re.sub(r'[^a-zA-Z\s]', ' ', slug.replace('-', ' ')).strip().title()
        return f"Candidate Name: {clean_name}\nNote: Profile data restricted."
    except:
        return "Candidate Name: Professional Candidate"
