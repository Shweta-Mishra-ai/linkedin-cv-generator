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
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find("meta", property="og:title")
        desc = soup.find("meta", property="og:description")

        data = ""
        if title and title.get("content"):
            data += f"NAME AND TITLE: {title.get('content')}\n"
        if desc and desc.get("content"):
            data += f"SUMMARY: {desc.get('content')}\n"

        if len(data) > 10 and "Sign In" not in data:
            return data
        else:
            return get_linkedin_fallback_data(url)
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    try:
        path = urllib.parse.urlparse(url).path
        slug = path.strip("/").split("/")[-1]
        clean_name = re.sub(r'[^a-zA-Z\s]', ' ', slug.replace('-', ' ')).strip().title()
        return f"NAME AND TITLE: {clean_name}\nSUMMARY: Public profile details are currently hidden due to LinkedIn privacy settings. Please upload your PDF resume to extract full data."
    except:
        return "NAME AND TITLE: Professional Candidate\nSUMMARY: Profile protected."
