import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    """Subah wala simple and effective URL fetcher"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", property="og:description")

        extracted_data = ""
        if meta_title and meta_title.get("content"):
            extracted_data += f"REAL NAME AND TITLE: {meta_title.get('content')}\n"
        if meta_desc and meta_desc.get("content"):
            extracted_data += f"REAL SUMMARY: {meta_desc.get('content')}\n"

        if len(extracted_data) > 10:
            return f"--- PUBLIC LINKEDIN DATA ---\n{extracted_data}"
        else:
            return get_linkedin_fallback_data(url)
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    try:
        path = urllib.parse.urlparse(url).path
        slug = path.strip("/").split("/")[-1]
        clean_name = re.sub(r'[^a-zA-Z\s]', ' ', slug.replace('-', ' ')).strip().title()
        return f"REAL NAME: {clean_name}\nNOTE: Full data blocked by LinkedIn."
    except:
        return "REAL NAME: Candidate"
