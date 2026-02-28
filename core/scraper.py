import PyPDF2
import requests
from bs4 import BeautifulSoup

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove scripts and styles for clean text
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        return text if text else "Could not extract text."
    except Exception as e:
        return f"Scraping failed: {str(e)}"

def get_linkedin_fallback_data(url):
    try:
        slug = url.strip("/").split("/")[-1]
        extracted_name = slug.replace("-", " ").title()
        return f"Name: {extracted_name}\nHeadline: Professional on LinkedIn"
    except:
        return "Name: LinkedIn User\nHeadline: Professional"
