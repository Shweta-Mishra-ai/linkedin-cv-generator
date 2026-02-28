import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    """General URL Scraper using SEO Meta-Tags to bypass security"""
    try:
        # Posing as Google Search Bot to force LinkedIn to show public meta-data
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 🌟 THE TRICK: Hunting for public SEO tags
        meta_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", property="og:description")

        extracted_info = ""
        if meta_title:
            extracted_info += f"Name and Title: {meta_title.get('content', '')}\n"
        if meta_desc:
            extracted_info += f"Headline and Summary: {meta_desc.get('content', '')}\n"

        # Also grab basic page text just in case
        for script in soup(["script", "style"]):
            script.decompose()
        body_text = soup.get_text(separator=' ', strip=True)

        if len(extracted_info) > 10:
            return f"--- PUBLIC META DATA ---\n{extracted_info}\n--- PAGE TEXT ---\n{body_text[:1500]}"
        elif len(body_text) > 200 and "authwall" not in response.url.lower():
            return body_text
        else:
            return get_linkedin_fallback_data(url)
    except Exception as e:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    """Extracts perfect name from URL if everything else fails"""
    try:
        path = urllib.parse.urlparse(url).path
        name_slug = path.strip("/").split("/")[-1]
        name = name_slug.replace("-", " ").title()
        if not name or name.lower() == "in":
            name = "Candidate"
        return f"Name: {name}\nNotice: Full data protected. Please use PDF upload for detailed experience."
    except:
        return "Name: Professional Candidate\nNotice: Could not extract data."
