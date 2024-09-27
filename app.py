import streamlit as st
from main_functions import ReggieResume
import logging

logging.basicConfig(level=logging.INFO)
reggie = ReggieResume()

st.title("AI Resume and Job Description Matcher")

# Input your full resume as text
st.markdown("### Input Your Resume")
resume_text = st.text_area("Paste your resume here:", height=400)

# Input the job description
st.markdown("### Input Job Description")
job_description = st.text_area("Paste the job description here:", height=400)

# Generate tailored resume based on the job description
if st.button("Generate Tailored Resume"):
    if not resume_text or not job_description:
        st.error("Please provide both your resume and the job description.")
    else:
        try:
            reggie.input_resume(resume_text)  # Input the full resume
            tailored_resume, docx_buffer = reggie.generate_resume(job_description)

            st.success("Tailored resume generated successfully!")
            st.subheader("Tailored Resume")
            st.text_area("Resume Content", tailored_resume, height=400)

            # Download buttons for PDF and DOCX
            pdf_buffer = reggie.generate_pdf(tailored_resume)
            st.download_button("Download PDF", data=pdf_buffer, file_name="tailored_resume.pdf", mime="application/pdf")
            st.download_button("Download DOCX", data=docx_buffer, file_name="tailored_resume.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logging.error(f"Error generating tailored resume: {e}")
