import PyPDF2
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import streamlit as st
import json

def extract_pdf_text(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    return "".join(page.extract_text() + "\n" for page in pdf_reader.pages)

def scrape_url_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.find("meta", property="og:title")
        meta_desc = soup.find("meta", property="og:description")

        data = ""
        if meta_title:
            data += f"Name/Title: {meta_title.get('content')}\n"
        if meta_desc:
            data += f"Summary: {meta_desc.get('content')}\n"

        for script in soup(["script", "style"]):
            script.decompose()
        page_text = soup.get_text(separator=' ', strip=True)

        return data + "\n" + page_text[:3000]
    except:
        return get_linkedin_fallback_data(url)

def get_linkedin_fallback_data(url):
    try:
        path = urllib.parse.urlparse(url).path
        slug = path.strip("/").split("/")[-1]
        clean_name = re.sub(r'[^a-zA-Z\s]', ' ', slug.replace('-', ' ')).strip().title()
        return f"REAL NAME: {clean_name}\nNOTE: Full profile blocked by LinkedIn login wall. Using limited title data."
    except:
        return "Name: Candidate"
