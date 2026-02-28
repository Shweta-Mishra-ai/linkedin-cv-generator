import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    try:
        # Google Bot trick to fetch Real Meta-Data from LinkedIn URL
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        }
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", property="og:description")

        extracted_info = ""
        if meta_title:
            extracted_info += f"Name and Title: {meta_title.get('content', '')}\n"
        if meta_desc:
            extracted_info += f"Headline and Summary: {meta_desc.get('content', '')}\n"

        if len(extracted_info) > 10:
            return f"--- URL META DATA ---\n{extracted_info}"
        else:
            return get_linkedin_fallback_data(url)
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    try:
        path = urllib.parse.urlparse(url).path
        name = path.strip("/").split("/")[-1].replace("-", " ").title()
        if not name or name.lower() == "in":
            name = "Professional Candidate"
        return f"Name: {name}\nHeadline: Professional looking for new opportunities."
    except:
        return "Name: Professional Candidate\nHeadline: Experienced Professional"
