<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f0c29,50:302b63,100:24243e&height=200&section=header&text=CareerForge%20AI&fontSize=60&fontColor=ffffff&fontAlignY=38&desc=LinkedIn%20Profile%20→%20Professional%20CV%20in%20Seconds&descAlignY=60&descSize=18&animation=fadeIn" width="100%"/>

<br/>

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge&logoColor=white)](https://linkedin-cv-generator-d4v5vnoshm4rzvnchamfqj.streamlit.app/)
[![Demo Video](https://img.shields.io/badge/📺_Demo_Video-Loom-625DF5?style=for-the-badge&logoColor=white)](https://www.loom.com/share/e5b1c8ffb00b447c90a910b9b27efe70)
[![GitHub Stars](https://img.shields.io/github/stars/Shweta-Mishra-ai/CareerForge_AI?style=for-the-badge&logo=github&color=f0c040&labelColor=1a1a2e)](https://github.com/Shweta-Mishra-ai/CareerForge_AI/stargazers)
[![Forks](https://img.shields.io/github/forks/Shweta-Mishra-ai/CareerForge_AI?style=for-the-badge&logo=github&color=4fc3f7&labelColor=1a1a2e)](https://github.com/Shweta-Mishra-ai/CareerForge_AI/network/members)
[![License: MIT](https://img.shields.io/badge/License-MIT-00e676?style=for-the-badge&labelColor=1a1a2e)](https://github.com/Shweta-Mishra-ai/CareerForge_AI/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a2e)](https://www.python.org/)

<br/>

> **Transform your raw LinkedIn profile into a polished, ATS-ready CV — powered by Google Gemini AI, with bulletproof anti-bot resilience.**

</div>

---

## 📌 Table of Contents

- [Why CareerForge AI?](#-why-careerforge-ai)
- [Live Demo](#-live-demo)
- [Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [Support the Project](#-support-the-project)

---

## 💡 Why CareerForge AI?

LinkedIn's anti-bot defenses (`HTTP 999`, `403 Forbidden`) are some of the most aggressive on the web. Cloud-hosted scrapers get IP-banned within seconds. Most CV generators either break silently or crash entirely.

**CareerForge AI solves this with a two-layer resilience strategy:**

| Layer | Method | Reliability |
|---|---|---|
| 🥇 **Primary** | Native LinkedIn PDF Upload | ✅ 100% — No network, no ban |
| 🥈 **Fallback** | Googlebot-spoofed URL scraper + slug parsing | ⚡ Best-effort, graceful degradation |

Once data is extracted — messy or clean — **Google Gemini 1.5 Flash** restructures it into a perfect JSON schema. The result is a **print-ready, Canva-quality HTML CV** you can save as a PDF instantly.

---

## 🌐 Live Demo

> 🔗 **[Try it live → linkedin-cv-generator.streamlit.app](https://linkedin-cv-generator-d4v5vnoshm4rzvnchamfqj.streamlit.app/)**

> 📺 **[Watch the walkthrough on Loom](https://www.loom.com/share/e5b1c8ffb00b447c90a910b9b27efe70)**

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT LAYER                         │
│                                                                 │
│    ┌──────────────────────┐    ┌──────────────────────────┐    │
│    │  📄 LinkedIn PDF     │    │  🔗 LinkedIn Profile URL │    │
│    │  (Primary — 100%)    │    │  (Fallback — Best Effort)│    │
│    └──────────┬───────────┘    └─────────────┬────────────┘    │
└───────────────┼─────────────────────────────┼─────────────────┘
                │                             │
                ▼                             ▼
┌──────────────────────────────────────────────────────────────┐
│                     EXTRACTION LAYER                         │
│                                                              │
│   ┌────────────────┐          ┌──────────────────────────┐  │
│   │  PyPDF2        │          │  BeautifulSoup4 +         │  │
│   │  Text Parser   │          │  Requests (Googlebot UA) │  │
│   └───────┬────────┘          └────────────┬─────────────┘  │
│           └────────────┬───────────────────┘                │
└────────────────────────┼───────────────────────────────────┘
                         │  Raw Unstructured Text
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                      AI ENGINE LAYER                         │
│                                                              │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  Google Gemini 1.5 Flash / Gemini Pro                │  │
│   │                                                      │  │
│   │  Prompt: "Extract structured CV data as JSON"        │  │
│   │  Output: { name, headline, skills[], experience[] }  │  │
│   │  Fallback LLM: Groq (xAI Grok) on API timeout       │  │
│   └────────────────────────┬─────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────┘
                             │  Clean JSON Schema
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    CV GENERATION LAYER                       │
│                                                              │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  HTML/CSS Template Engine                            │  │
│   │  • Canva-style layout  • Dark/Light mode             │  │
│   │  • Base64 encoded for direct browser download        │  │
│   └────────────────────────┬─────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
                    📥 Download CV (HTML → PDF via Ctrl+P)
```

---

## ✨ Key Features

### 🛡️ Anti-Bot Resilience
LinkedIn's `HTTP 999` and `403` errors are handled proactively. The app **never crashes** — it degrades gracefully from URL scraping to PDF upload with clear user guidance.

### 🧠 AI-Powered Extraction (Gemini 1.5 Flash)
Raw, unstructured LinkedIn text — with inconsistent formatting, emojis, and section bleed — is transformed into a clean JSON schema using Gemini's language understanding. Groq (Grok) serves as a fast fallback if Gemini hits rate limits.

### 🎨 Premium CV Template
Not just text dumped into a box. The output is a structured, typography-forward HTML resume — styled for print — with sections for Summary, Experience, Skills, Education, and Certifications.

### 📎 Chrome Extension Support
A companion Chrome Extension (`/chrome_extension`) allows users to capture their LinkedIn profile directly from the browser, eliminating the need for manual PDF export.

### 🎯 ATS Optimization Mode
Paste a job description or JD URL alongside your LinkedIn data to receive a tailored, keyword-optimized CV aligned with Applicant Tracking System criteria.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend / Hosting** | Streamlit | UI & Cloud Deployment |
| **PDF Parsing** | PyPDF2 | Primary data extraction |
| **Web Scraping** | BeautifulSoup4, Requests | URL fallback extraction |
| **AI Engine** | Google Gemini 1.5 Flash | JSON structuring from raw text |
| **Fallback LLM** | Groq (xAI Grok) | Rate-limit resilience |
| **CV Rendering** | HTML5 / CSS3 | Print-ready output |
| **Distribution** | Base64 Encoding | In-browser file download |
| **Browser Tool** | Chrome Extension (JS) | Direct LinkedIn capture |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Gemini API Key → [Get yours here](https://makersuite.google.com/app/apikey)

### 1. Clone & Install

```bash
git clone https://github.com/Shweta-Mishra-ai/CareerForge_AI.git
cd CareerForge_AI
pip install -r requirements.txt
```

### 2. Configure API Key

Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
# Optional: Groq fallback
GROQ_API_KEY = "your_groq_api_key_here"
```

### 3. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🎯 How It Works

```
Step 1 → Upload LinkedIn PDF  (from LinkedIn → Me → Save to PDF)
           OR paste your LinkedIn profile URL

Step 2 → (Optional) Paste a Job Description for ATS targeting

Step 3 → Click "Analyze & Generate"
           AI extracts → structures → templates your data

Step 4 → Download your CV as HTML
           Save as PDF: Ctrl+P → Save as PDF (Chrome recommended)
```

---

## 📁 Project Structure

```
CareerForge_AI/
│
├── .streamlit/
│   └── secrets.toml          # API keys (not committed)
│
├── chrome_extension/         # Browser extension for direct LinkedIn capture
│   ├── manifest.json
│   ├── content.js
│   └── popup.html
│
├── core/                     # Business logic (no Streamlit imports here)
│   ├── extractor.py          # PDF + URL extraction pipeline
│   ├── ai_engine.py          # Gemini + Groq LLM orchestration
│   └── cv_builder.py         # HTML/CSS template renderer
│
├── templates/                # CV HTML/CSS templates
│
├── app.py                    # Streamlit entry point
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🗺️ Roadmap

| Status | Feature |
|---|---|
| ✅ Done | PDF upload extraction |
| ✅ Done | Gemini AI structuring |
| ✅ Done | HTML CV generation |
| ✅ Done | Streamlit Cloud deployment |
| ✅ Done | Chrome Extension (beta) |
| ✅ Done | Groq fallback LLM |
| 🔄 In Progress | Multiple CV template styles |
| 🔄 In Progress | ATS score analyzer |
| 📋 Planned | LinkedIn OAuth (official API) |
| 📋 Planned | Resume → LinkedIn Profile (reverse mode) |
| 📋 Planned | DOCX export support |
| 📋 Planned | Cover Letter generator |

---

## 🤝 Contributing

Contributions are very welcome. Here's how to get started:

```bash
# Fork the repo, then:
git clone https://github.com/YOUR_USERNAME/CareerForge_AI.git
git checkout -b feature/your-feature-name

# Make your changes, then:
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
# Open a Pull Request
```

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages (`feat:`, `fix:`, `docs:`, `refactor:`).

For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

Distributed under the **MIT License** — free for personal, commercial, and portfolio use.
See [`LICENSE`](https://github.com/Shweta-Mishra-ai/CareerForge_AI/blob/main/LICENSE) for full terms.

---

## ⭐ Support the Project

If CareerForge AI saved you time or helped your job search, the best way to support is:

```
⭐ Star this repository — it helps more job seekers discover this tool
🍴 Fork it — customize it, build on it, make it yours
🐛 Open an Issue — found a bug? your report makes it better for everyone
📢 Share it — LinkedIn, Twitter, Discord, wherever developers gather
```

---

<div align="center">

**Built for job seekers, by a job seeker.**

*Open source. Free forever.*

[![Star History Chart](https://api.star-history.com/svg?repos=Shweta-Mishra-ai/CareerForge_AI&type=Date)](https://star-history.com/#Shweta-Mishra-ai/CareerForge_AI)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:24243e,50:302b63,100:0f0c29&height=120&section=footer" width="100%"/>

</div>
