import streamlit as st
import openai
from PIL import Image
from main_functions import (
    analyze_resume_and_job,
    generate_full_resume,
    generate_cover_letter,
    generate_follow_up_message,
    create_pdf
)
import os

# Set up OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

st.set_page_config(page_title="AI Resume Tailor", page_icon="📄", layout="wide")

# Load and display the logo alongside the title
col1, col2 = st.columns([1, 12])
with col1:
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        logo = Image.open(logo_path)
        st.image(logo, width=100)
    except FileNotFoundError:
        st.warning("Logo image not found. Please ensure 'logo.png' is in the project directory.")
with col2:
    st.title("AI Resume Tailor")

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None

def sanitize_for_pdf(text):
    return ''.join(char for char in text if ord(char) < 128)

col1, col2 = st.columns(2)
with col1:
    resume = st.text_area("Paste your resume here", height=300)
with col2:
    job_description = st.text_area("Paste the job description here", height=300)

def generate_resume():
    if resume and job_description:
        try:
            with st.spinner("Analyzing and tailoring your resume..."):
                analysis = analyze_resume_and_job(resume, job_description)
                if analysis:
                    header, summary, comparison, education, work_experience, cover_letter_info, ats_keywords = analysis
                    company_name = cover_letter_info['Company Name']
                    full_resume = generate_full_resume(header, summary, comparison, education, work_experience, company_name)
                    
                    st.session_state.resume_data = {
                        'header': header,
                        'summary': summary,
                        'comparison': comparison,
                        'education': education,
                        'work_experience': work_experience,
                        'full_resume': full_resume,
                        'cover_letter_info': cover_letter_info,
                        'ats_keywords': ats_keywords
                    }
                    st.session_state.generated = True
                else:
                    st.error("Failed to analyze the resume and job description.")
        except Exception as e:
            st.error(f"An error occurred during generation: {str(e)}")
    else:
        st.warning("Please provide both your resume and the job description.")

if st.button("Analyze and Tailor Resume"):
    generate_resume()

if st.session_state.generated:
    data = st.session_state.resume_data
    
    st.subheader("ATS Keywords Extracted")
    st.info(", ".join(data['ats_keywords']))
    
    st.subheader("Tailored Header")
    st.info(data['header'])
    
    st.subheader("Custom Summary")
    st.success(data['summary'])
    
    st.subheader("Skills Comparison")
    comp_col1, comp_col2 = st.columns(2)
    with comp_col1:
        st.markdown("**Your Skills & Experience**")
        for skill in data['comparison'][0]:
            st.write(f"• {skill}")
    with comp_col2:
        st.markdown("**Job Requirements**")
        for req in data['comparison'][1]:
            st.write(f"• {req}")
    
    st.subheader("Education")
    st.write(data['education'])
    
    st.subheader("Relevant Work Experience")
    st.write(data['work_experience'])
    
    st.subheader("Complete Tailored Resume")
    st.text_area("Copy and edit your tailored resume:", data['full_resume'], height=400)
    st.info("Please review and edit the generated resume to ensure all information is accurate and fits on one page. You may need to adjust the work experience and education sections.")
    
    # Cover Letter Section
    st.subheader("Generate Cover Letter")
    cover_letter_col1, cover_letter_col2 = st.columns([1, 1])
    with cover_letter_col1:
        tone = st.selectbox(
            "Select Cover Letter Tone",
            options=["professional", "confident", "enthusiastic", "witty"],
            index=0
        )
    with cover_letter_col2:
        generate_cl = st.button("Generate Cover Letter")
    
    if generate_cl:
        with st.spinner("Generating cover letter..."):
            cover_letter = generate_cover_letter(
                resume=data['full_resume'],
                job_description=job_description,
                cover_letter_info=data['cover_letter_info'],
                tone=tone
            )
            if cover_letter:
                data['cover_letter'] = cover_letter
                st.session_state.resume_data = data
                st.success("Cover letter generated successfully!")
            else:
                st.error("Failed to generate cover letter.")
    
    if 'cover_letter' in data:
        st.subheader("Cover Letter")
        st.text_area("Copy your cover letter:", data['cover_letter'], height=300)
    
    # Follow-Up Message Section
    st.subheader("Generate Follow-Up Message")
    follow_up_option = st.checkbox("Generate Follow-Up Message")
    if follow_up_option:
        custom_follow_up = st.text_area("Customize your Follow-Up Message (optional)", height=100)
        follow_up_col1, follow_up_col2 = st.columns([1, 1])
        with follow_up_col1:
            generate_fu = st.button("Generate Follow-Up Message")
        if generate_fu:
            with st.spinner("Generating follow-up message..."):
                follow_up_message = generate_follow_up_message(
                    resume=resume,
                    job_description=job_description,
                    cover_letter_info=data['cover_letter_info'],
                    custom_message=custom_follow_up if custom_follow_up else None
                )
                if follow_up_message:
                    data['follow_up_message'] = follow_up_message
                    st.session_state.resume_data = data
                    st.success("Follow-up message generated successfully!")
                else:
                    st.error("Failed to generate follow-up message.")
    
    if 'follow_up_message' in data:
        st.subheader("Follow-Up Message")
        st.text_area("Copy your follow-up message:", data['follow_up_message'], height=200)
    
        # Optionally, allow downloading the follow-up message as PDF
        with st.expander("Download Follow-Up Message as PDF"):
            try:
                create_pdf(sanitize_for_pdf(data['follow_up_message']), "follow_up_message.pdf")
                with open("follow_up_message.pdf", "rb") as pdf_file:
                    PDFbyte = pdf_file.read()
                st.download_button(
                    label="Download Follow-Up Message PDF",
                    data=PDFbyte,
                    file_name="follow_up_message.pdf",
                    mime='application/octet-stream'
                )
            except Exception as e:
                st.error(f"An error occurred while creating the follow-up PDF: {str(e)}")
    
    # Generate PDF downloads for Resume and Cover Letter
    if 'cover_letter' in data:
        st.subheader("Download Documents as PDF")
        pdf_col1, pdf_col2, pdf_col3 = st.columns(3)
        with pdf_col1:
            try:
                create_pdf(sanitize_for_pdf(data['full_resume']), "tailored_resume.pdf")
                with open("tailored_resume.pdf", "rb") as pdf_file:
                    PDFbyte = pdf_file.read()
                st.download_button(
                    label="Download Resume PDF",
                    data=PDFbyte,
                    file_name="tailored_resume.pdf",
                    mime='application/octet-stream'
                )
            except Exception as e:
                st.error(f"An error occurred while creating the resume PDF: {str(e)}")
        
        with pdf_col2:
            try:
                create_pdf(sanitize_for_pdf(data['cover_letter']), "cover_letter.pdf")
                with open("cover_letter.pdf", "rb") as pdf_file:
                    PDFbyte = pdf_file.read()
                st.download_button(
                    label="Download Cover Letter PDF",
                    data=PDFbyte,
                    file_name="cover_letter.pdf",
                    mime='application/octet-stream'
                )
            except Exception as e:
                st.error(f"An error occurred while creating the cover letter PDF: {str(e)}")
        
        # Follow-Up Message PDF is handled above
    
    # Start Over Button
    if st.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()
    
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and OpenAI GPT-4")
