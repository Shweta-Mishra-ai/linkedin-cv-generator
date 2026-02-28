import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    """
    ULTIMATE REAL DATA FETCHER: 
    Bypasses LinkedIn wall by fetching data from Public Search Engines & SEO Tags!
    """
    real_data = ""
    try:
        # 1. Fetch from DuckDuckGo/Google Public Search Snippets
        search_query = urllib.parse.quote(url)
        search_url = f"https://html.duckduckgo.com/html/?q={search_query}"
        search_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        search_res = requests.get(search_url, headers=search_headers, timeout=8)
        search_soup = BeautifulSoup(search_res.text, 'html.parser')
        
        # Extract the exact search engine snippet which holds real job data
        snippet = search_soup.find('a', class_='result__snippet')
        if snippet:
            real_data += f"Public Search Profile Summary: {snippet.text}\n\n"

        # 2. Fetch LinkedIn's Public SEO Meta Tags (acting as GoogleBot)
        li_headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        li_res = requests.get(url, headers=li_headers, timeout=8)
        li_soup = BeautifulSoup(li_res.text, 'html.parser')

        meta_title = li_soup.find("meta", property="og:title")
        meta_desc = li_soup.find("meta", property="og:description")
        
        if meta_title:
            real_data += f"LinkedIn Title: {meta_title.get('content', '')}\n"
        if meta_desc:
            real_data += f"LinkedIn Description: {meta_desc.get('content', '')}\n"

        if len(real_data.strip()) > 15:
            return f"--- REAL PUBLIC DATA ---\n{real_data}"
        else:
            return get_linkedin_fallback_data(url)
    except Exception as e:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    # Basic fallback if internet/search fails
    try:
        path = urllib.parse.urlparse(url).path
        slug = path.strip("/").split("/")[-1]
        clean_name = re.sub(r'[^a-zA-Z\s]', ' ', slug.replace('-', ' ')).strip().title()
        return f"Name: {clean_name}\nNotice: Only URL name available."
    except:
        return "Name: Professional Candidate"
