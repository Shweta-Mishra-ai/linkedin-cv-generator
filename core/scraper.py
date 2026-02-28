import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    """General URL Scraper for any candidate"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers, timeout=8)
        
        # If LinkedIn throws a security wall (Status 999) or redirects to login
        if response.status_code != 200 or "authwall" in response.url.lower():
            return get_linkedin_fallback_data(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        
        # If text is too short, it means we hit a privacy block
        if len(text) < 200 or "security" in text.lower() or "sign in" in text.lower():
            return get_linkedin_fallback_data(url)
            
        return text
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    """Honest Fallback for Recruiters when LinkedIn blocks access"""
    try:
        path = urllib.parse.urlparse(url).path
        name_slug = path.strip("/").split("/")[-1]
        name = name_slug.replace("-", " ").title()
        if not name or name.lower() == "in":
            name = "Candidate"
    except:
        name = "Candidate"
        
    # Strictly telling the AI and the App that data is blocked, do not hallucinate.
    return f"""
    Name: {name}
    Headline: Profile Data Protected by LinkedIn
    Notice: LinkedIn Privacy Wall Blocked Extraction.
    Experience: <p><i>Public profile scraping blocked by LinkedIn security. To run an accurate ATS analysis, please use the 'Upload PDF' method.</i></p>
    Skills: Not Available
    Education: <p><i>Not Available</i></p>
    Certificates: <p><i>Not Available</i></p>
    """
