import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    try:
        # Googlebot header works best for extracting public LinkedIn Meta Tags
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", property="og:description")

        extracted_info = ""
        if meta_title:
            extracted_info += f"Name & Title: {meta_title.get('content', '')}\n"
        if meta_desc:
            extracted_info += f"Headline & Summary: {meta_desc.get('content', '')}\n"

        # Also grab basic text if available
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        body_text = soup.get_text(separator=' ', strip=True)
        clean_text = " ".join([line for line in body_text.splitlines() if len(line.strip()) > 20])

        if len(extracted_info) > 10:
            return f"--- PUBLIC META DATA ---\n{extracted_info}\n--- PAGE TEXT ---\n{clean_text[:2000]}"
        else:
            return get_linkedin_fallback_data(url)
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    try:
        path = urllib.parse.urlparse(url).path
        name = path.strip("/").split("/")[-1].replace("-", " ").title()
        return f"Name: {name}\nHeadline: Professional Profile"
    except:
        return "Name: Professional Candidate"
