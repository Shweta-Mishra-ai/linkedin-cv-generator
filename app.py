import streamlit as st
import json
import base64

st.set_page_config(page_title="LinkedIn to CV Generator", page_icon="📄")

st.title("📄 LinkedIn Profile to CV Generator")
st.markdown("Upload your extracted LinkedIn JSON data, and we'll format it into a professional CV.")

# Toggle for Mock Data
use_mock = st.toggle("Use Mock Dataset (Demo Mode)")

if use_mock:
    # A simple mock dataset for demonstration
    profile_data = {
        "name": "Jane Doe",
        "headline": "Full Stack Engineer | React & Python",
        "experience": ["Senior Developer at TechCorp", "Junior Dev at Startup Inc"],
        "education": ["B.S. Computer Science, State University"]
    }
    st.success("Loaded Mock Data!")
else:
    # File upload for real extracted JSON
    uploaded_file = st.file_uploader("Upload LinkedIn profile.json", type=['json'])
    if uploaded_file is not None:
        profile_data = json.load(uploaded_file)
        st.success("Loaded Custom Data!")
    else:
        profile_data = None

# Display Data & Generate
if profile_data:
    st.subheader("Extracted Profile Data:")
    st.json(profile_data)
    
    st.markdown("---")
    
    if st.button("Generate PDF CV", type="primary"):
        # In a real app, you would pass data to FPDF or python-docx here.
        # For the demo, we create a dummy text file to simulate a download.
        dummy_cv_content = f"CV for {profile_data.get('name', 'User')}\n\nHeadline: {profile_data.get('headline', '')}"
        
        b64 = base64.b64encode(dummy_cv_content.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="generated_cv.txt">Click here to download your CV</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.balloons()
