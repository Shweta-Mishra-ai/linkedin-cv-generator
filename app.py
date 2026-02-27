import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import base64

st.set_page_config(page_title="LinkedIn Scraper & CV Generator", page_icon="🚀")

st.title("🚀 LinkedIn URL Scraper to CV")
st.markdown("Enter a LinkedIn Profile URL below to scrape public data and generate a CV.")

# URL Input
linkedin_url = st.text_input("🔗 Enter LinkedIn Profile URL:", placeholder="https://www.linkedin.com/in/username/")

# Helper function to scrape URL
def scrape_linkedin_profile(url):
    # Professional headers to avoid immediate bot detection
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # LinkedIn often returns 999 or 401 for bots.
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extracting basic info (Title tag usually contains Name and Headline)
            page_title = soup.find('title').get_text() if soup.find('title') else "Name Not Found"
            
            # Real extraction logic here
            profile_data = {
                "name": page_title.split('-')[0].strip(),
                "headline": "Professional from LinkedIn",
                "source": "Live Scraping",
                "raw_html_length": len(response.text)
            }
            return profile_data, True
        else:
            return None, False
    except Exception as e:
        return None, False

# Helper function to generate a simple text CV (You can replace this with python-docx later)
def generate_cv_download(data):
    cv_content = f"================================\n"
    cv_content += f"      CURRICULUM VITAE          \n"
    cv_content += f"================================\n\n"
    cv_content += f"Name: {data.get('name', 'N/A')}\n"
    cv_content += f"Headline: {data.get('headline', 'N/A')}\n\n"
    cv_content += f"Data Source: {data.get('source', 'Unknown')}\n"
    cv_content += f"\n[This CV was automatically generated from scraped data.]"
    
    b64 = base6
