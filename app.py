import streamlit as st
import openai
from main_functions import analyze_resume_and_job, generate_full_resume, generate_cover_letter, create_pdf

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
                header, summary, comparison, education, work_experience = analyze_resume_and_job(resume, job_description)
                
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
                
                st.subheader("Education")
                st.write(education)
                
                st.subheader("Relevant Work Experience")
                st.write(work_experience)
                
                st.subheader("Complete Tailored Resume")
                full_resume = generate_full_resume(header, summary, comparison, education, work_experience)
                st.text_area("Copy and edit your tailored resume:", full_resume, height=400)
                st.info("Please review and edit the generated resume to ensure all information is accurate and fits on one page. You may need to adjust the work experience and education sections.")
                
                st.subheader("Cover Letter")
                cover_letter = generate_cover_letter(resume, job_description)
                st.text_area("Copy your cover letter:", cover_letter, height=300)

                # Generate PDF downloads
                create_pdf(full_resume, "tailored_resume.pdf")
                create_pdf(cover_letter, "cover_letter.pdf")

                col1, col2 = st.columns(2)
                with col1:
                    with open("tailored_resume.pdf", "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    st.download_button(label="Download Resume as PDF",
                                       data=PDFbyte,
                                       file_name="tailored_resume.pdf",
                                       mime='application/octet-stream')
                
                with col2:
                    with open("cover_letter.pdf", "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    st.download_button(label="Download Cover Letter as PDF",
                                       data=PDFbyte,
                                       file_name="cover_letter.pdf",
                                       mime='application/octet-stream')

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please provide both your resume and the job description.")

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and OpenAI GPT-4")
