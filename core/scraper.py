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
        # Standard browser headers to fetch Link Previews
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract EXACT Public SEO Data
        meta_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", property="og:description")

        real_data = ""
        if meta_title and meta_title.get("content"):
            real_data += f"REAL HEADLINE/TITLE: {meta_title.get('content')}\n"
        if meta_desc and meta_desc.get("content"):
            real_data += f"REAL ABOUT/SUMMARY: {meta_desc.get('content')}\n"

        if len(real_data) > 10:
            return f"--- EXACT PUBLIC LINKEDIN DATA ---\n{real_data}"
        else:
            return get_linkedin_fallback_data(url)
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    try:
        path = urllib.parse.urlparse(url).path
        slug = path.strip("/").split("/")[-1]
        clean_name = re.sub(r'[^a-zA-Z\s]', ' ', slug.replace('-', ' ')).strip().title()
        return f"REAL NAME: {clean_name}\nNOTE: Full profile blocked by LinkedIn login wall."
    except:
        return "REAL NAME: Candidate"
