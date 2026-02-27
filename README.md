# 🚀 AI-Powered LinkedIn to CV Generator

A smart, resilient, and beautifully designed web application built with Streamlit and Google's Gemini AI. This tool extracts unstructured data from LinkedIn profiles and converts it into a professional, print-ready HTML CV.

**🌐 Live Demo:** [View the App on Streamlit](https://linkedin-cv-generator-d4v5vnoshm4rzvnchamfqj.streamlit.app/)

---

## ✨ Key Features

* **📄 Bulletproof PDF Parsing:** Bypass LinkedIn's strict anti-bot mechanisms entirely by uploading a native LinkedIn Profile PDF export. 100% reliable.
* **🔗 Smart URL Scraping:** Features an intelligent URL scraper that uses Googlebot header spoofing and URL slug parsing as a fallback if LinkedIn blocks the request.
* **🧠 AI-Driven Extraction:** Powered by Google's Gemini API (`gemini-pro` / `gemini-1.5-flash`) to intelligently read raw, messy text and structure it into perfect JSON (Name, Headline, Skills, Experience).
* **🎨 Pro-Level Design Template:** Does not just dump plain text. It generates a beautifully formatted, Canva-style HTML resume that is instantly ready to be saved as a PDF (Ctrl+P).

---

## 🛠️ Architecture & Tech Stack

* **Frontend & Hosting:** Streamlit (Python)
* **Data Extraction:** BeautifulSoup4, Requests
* **PDF Processing:** PyPDF2
* **AI Engine:** Google Generative AI (Gemini API)
* **Document Generation:** HTML/CSS with Base64 encoding for direct downloads

---

## 🚀 How to Run Locally

1. **Clone the repository:**
   `git clone https://github.com/Shweta-Mishra-ai/linkedin-cv-generator.git`
   `cd linkedin-cv-generator`

2. **Install dependencies:**
   `pip install -r requirements.txt`

3. **Set up your API Key:**
   Create a `.streamlit/secrets.toml` file in the root directory and add your Google Gemini API key:
   `GEMINI_API_KEY = "your_api_key_here"`

4. **Run the application:**
   `streamlit run app.py`

---

## 🧠 Note on Architecture (Why This Approach?)
Directly scraping LinkedIn URLs from a cloud server often results in immediate IP bans (HTTP 999/403 errors). To solve this real-world engineering problem, this application prioritizes the **PDF Upload method** for guaranteed 100% uptime, while maintaining a smart **URL Parsing fallback** to fulfill basic scraping requirements without crashing the app.
