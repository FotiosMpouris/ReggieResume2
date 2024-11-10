import streamlit as st

# Debug logging at start
st.write("App is starting...")

# Basic page config
st.set_page_config(page_title="AI Resume Tailor", page_icon="📄", layout="wide")

try:
    # Test OpenAI setup
    import openai
    st.write("OpenAI imported")
    openai.api_key = st.secrets["openai_api_key"]
    st.write("API key loaded")
    
    # Test basic UI
    st.title("AI Resume Tailor")
    
    # Test basic input
    col1, col2 = st.columns(2)
    with col1:
        resume = st.text_area("Test Resume Input", height=300)
    with col2:
        job_description = st.text_area("Test Job Description Input", height=300)
        
    if st.button("Test Button"):
        st.write("Button clicked!")
        
except Exception as e:
    st.error(f"Error occurred: {e}")
    st.error("Full error:", exception=True)  # This will show the full traceback

# Add a final message to see if we get this far
st.write("App finished loading")
