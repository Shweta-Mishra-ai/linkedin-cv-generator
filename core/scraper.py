import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        
        if len(text) < 200 or "security" in text.lower() or "auth" in text.lower():
            return get_linkedin_fallback_data(url)
        return text
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    try:
        path = urllib.parse.urlparse(url).path
        name = path.strip("/").split("/")[-1].replace("-", " ").title()
        return f"Name: {name}\nNotice: LinkedIn blocked the data extraction for this URL. Please use the PDF Upload method for real data."
    except:
        return "Name: Private User\nNotice: Please use PDF upload."
