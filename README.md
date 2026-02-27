# LinkedIn to CV Generator

This application takes structured JSON data extracted from a LinkedIn profile and formats it into a downloadable CV.

## Architecture & Approach
To bypass aggressive anti-bot measures and IP bans commonly associated with server-side LinkedIn scraping, this project adopts a decoupled, pragmatic approach:
1. **Extraction:** A client-side script (not included in this repo) runs in the browser console to extract legitimate DOM data into a `profile.json` file.
2. **Generation:** This Streamlit application consumes that JSON to generate the final document. 
3. **Demo Mode:** A mock dataset is included to demonstrate the generation logic without needing an active LinkedIn session.

## Run Locally
1. `pip install -r requirements.txt`
2. `streamlit run app.py`
