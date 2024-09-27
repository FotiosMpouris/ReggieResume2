import streamlit as st
import openai
from main_functions import analyze_resume_and_job

# Set up OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

st.title("AI Resume Tailor")

# Input fields
resume = st.text_area("Paste your resume here", height=300)
job_description = st.text_area("Paste the job description here", height=200)

if st.button("Analyze and Tailor Resume"):
    if resume and job_description:
        with st.spinner("Analyzing and tailoring your resume..."):
            header, summary, comparison = analyze_resume_and_job(resume, job_description)
            
            st.subheader("Tailored Header")
            st.write(header)
            
            st.subheader("Custom Summary")
            st.write(summary)
            
            st.subheader("Skills Comparison")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Your Skills & Experience**")
                st.write(comparison[0])
            with col2:
                st.markdown("**Job Requirements**")
                st.write(comparison[1])
    else:
        st.warning("Please provide both your resume and the job description.")
