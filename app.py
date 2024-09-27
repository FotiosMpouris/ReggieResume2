import streamlit as st
import openai
from main_functions import analyze_resume_and_job

# Set up OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

st.set_page_config(page_title="AI Resume Tailor", page_icon="📄", layout="wide")

st.title("AI Resume Tailor")

col1, col2 = st.columns(2)

with col1:
    resume = st.text_area("Paste your resume here", height=300)

with col2:
    job_description = st.text_area("Paste the job description here", height=300)

if st.button("Analyze and Tailor Resume"):
    if resume and job_description:
        try:
            with st.spinner("Analyzing and tailoring your resume..."):
                header, summary, comparison = analyze_resume_and_job(resume, job_description)
                
                st.subheader("Tailored Header")
                st.info(header)
                
                st.subheader("Custom Summary")
                st.success(summary)
                
                st.subheader("Skills Comparison")
                comp_col1, comp_col2 = st.columns(2)
                with comp_col1:
                    st.markdown("**Your Skills & Experience**")
                    for skill in comparison[0]:
                        st.write(f"• {skill}")
                with comp_col2:
                    st.markdown("**Job Requirements**")
                    for req in comparison[1]:
                        st.write(f"• {req}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please provide both your resume and the job description.")

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and OpenAI GPT-4")
