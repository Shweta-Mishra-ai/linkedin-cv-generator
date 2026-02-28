import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    """Deep Scraper: Fetches Meta Data + All Public Visible Text"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        extracted_data = []

        # 1. Guaranteed Data: SEO Meta Tags (Name, Headline, About)
        meta_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", property="og:description")
        
        if meta_title:
            extracted_data.append(f"Name & Title: {meta_title.get('content', '')}")
        if meta_desc:
            extracted_data.append(f"Headline & About: {meta_desc.get('content', '')}")

        # 2. Deep Data: Try to grab actual visible page text (Experience/Education)
        for element in soup(["script", "style", "nav", "footer", "noscript", "header"]):
            element.decompose() # Remove junk code
            
        page_text = soup.get_text(separator='\n', strip=True)
        
        # Filter out generic LinkedIn login warnings to keep data clean
        clean_lines = [line for line in page_text.split('\n') if len(line) > 15 and "Agree & Join" not in line and "Sign in" not in line]
        
        if clean_lines:
            extracted_data.append("--- PAGE CONTENT (Experience/Education) ---")
            extracted_data.append("\n".join(clean_lines[:100]))

        final_text = "\n".join(extracted_data)

        if len(final_text) > 20:
            return final_text
        else:
            return get_linkedin_fallback_data(url)
    except Exception as e:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    try:
        path = urllib.parse.urlparse(url).path
        name = path.strip("/").split("/")[-1].replace("-", " ").title()
        if not name or name.lower() == "in":
            name = "Professional Candidate"
        return f"Name: {name}\nNotice: This profile's details are completely hidden by LinkedIn privacy settings."
    except:
        return "Name: Professional Candidate\nNotice: Data restricted."
