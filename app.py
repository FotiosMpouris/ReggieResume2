import streamlit as st
import openai
from main_functions import analyze_resume_and_job, create_pdf, generate_cover_letter

# Set up OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

st.set_page_config(page_title="AI Resume Tailor", page_icon="📄", layout="wide")
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
                tailored_resume = analyze_resume_and_job(resume, job_description)
                cover_letter = generate_cover_letter(resume, job_description)
                
                st.session_state.resume_data = {
                    'tailored_resume': tailored_resume,
                    'cover_letter': cover_letter
                }
                st.session_state.generated = True
        except Exception as e:
            st.error(f"An error occurred during generation: {str(e)}")
    else:
        st.warning("Please provide both your resume and the job description.")

if st.button("Analyze and Tailor Resume"):
    generate_resume()

if st.session_state.generated:
    data = st.session_state.resume_data
    
    st.subheader("Tailored Resume")
    st.text_area("Copy and edit your tailored resume:", data['tailored_resume'], height=400)
    st.info("Please review and edit the generated resume to ensure all information is accurate and fits on one page.")
    
    st.subheader("Cover Letter")
    st.text_area("Copy your cover letter:", data['cover_letter'], height=300)

    # Generate PDF downloads
    try:
        create_pdf(sanitize_for_pdf(data['tailored_resume']), "tailored_resume.pdf")
        create_pdf(sanitize_for_pdf(data['cover_letter']), "cover_letter.pdf")

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
        st.error(f"An error occurred while creating PDFs: {str(e)}")

if st.button("Start Over"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and OpenAI GPT-4")

# import streamlit as st
# import openai
# from main_functions import analyze_resume_and_job, generate_full_resume, generate_cover_letter, create_pdf

# # Set up OpenAI API key
# openai.api_key = st.secrets["openai_api_key"]

# st.set_page_config(page_title="AI Resume Tailor", page_icon="📄", layout="wide")
# st.title("AI Resume Tailor")

# # Initialize session state
# if 'generated' not in st.session_state:
#     st.session_state.generated = False
# if 'resume_data' not in st.session_state:
#     st.session_state.resume_data = None

# def sanitize_for_pdf(text):
#     return ''.join(char for char in text if ord(char) < 128)

# col1, col2 = st.columns(2)
# with col1:
#     resume = st.text_area("Paste your resume here", height=300)
# with col2:
#     job_description = st.text_area("Paste the job description here", height=300)

# def generate_resume():
#     if resume and job_description:
#         try:
#             with st.spinner("Analyzing and tailoring your resume..."):
#                 header, summary, comparison, education, work_experience = analyze_resume_and_job(resume, job_description)
#                 full_resume = generate_full_resume(header, summary, comparison, education, work_experience)
#                 cover_letter = generate_cover_letter(resume, job_description)
                
#                 st.session_state.resume_data = {
#                     'header': header,
#                     'summary': summary,
#                     'comparison': comparison,
#                     'education': education,
#                     'work_experience': work_experience,
#                     'full_resume': full_resume,
#                     'cover_letter': cover_letter
#                 }
#                 st.session_state.generated = True
#         except Exception as e:
#             st.error(f"An error occurred during generation: {str(e)}")
#     else:
#         st.warning("Please provide both your resume and the job description.")

# if st.button("Analyze and Tailor Resume"):
#     generate_resume()

# if st.session_state.generated:
#     data = st.session_state.resume_data
    
#     st.subheader("Tailored Header")
#     st.info(data['header'])
    
#     st.subheader("Custom Summary")
#     st.success(data['summary'])
    
#     st.subheader("Skills Comparison")
#     comp_col1, comp_col2 = st.columns(2)
#     with comp_col1:
#         st.markdown("**Your Skills & Experience**")
#         for skill in data['comparison'][0]:
#             st.write(f"• {skill}")
#     with comp_col2:
#         st.markdown("**Job Requirements**")
#         for req in data['comparison'][1]:
#             st.write(f"• {req}")
    
#     st.subheader("Education")
#     st.write(data['education'])
    
#     st.subheader("Relevant Work Experience")
#     st.write(data['work_experience'])
    
#     st.subheader("Complete Tailored Resume")
#     st.text_area("Copy and edit your tailored resume:", data['full_resume'], height=400)
#     st.info("Please review and edit the generated resume to ensure all information is accurate and fits on one page. You may need to adjust the work experience and education sections.")
    
#     st.subheader("Cover Letter")
#     st.text_area("Copy your cover letter:", data['cover_letter'], height=300)

#     # Generate PDF downloads
#     try:
#         create_pdf(sanitize_for_pdf(data['full_resume']), "tailored_resume.pdf")
#         create_pdf(sanitize_for_pdf(data['cover_letter']), "cover_letter.pdf")

#         col1, col2 = st.columns(2)
#         with col1:
#             with open("tailored_resume.pdf", "rb") as pdf_file:
#                 PDFbyte = pdf_file.read()
#             st.download_button(label="Download Resume as PDF",
#                                data=PDFbyte,
#                                file_name="tailored_resume.pdf",
#                                mime='application/octet-stream')
        
#         with col2:
#             with open("cover_letter.pdf", "rb") as pdf_file:
#                 PDFbyte = pdf_file.read()
#             st.download_button(label="Download Cover Letter as PDF",
#                                data=PDFbyte,
#                                file_name="cover_letter.pdf",
#                                mime='application/octet-stream')
#     except Exception as e:
#         st.error(f"An error occurred while creating PDFs: {str(e)}")

# if st.button("Start Over"):
#     for key in list(st.session_state.keys()):
#         del st.session_state[key]
#     st.experimental_rerun()

# st.markdown("---")
# st.markdown("Built with ❤️ using Streamlit and OpenAI GPT-4")

# import streamlit as st
# import openai
# from main_functions import analyze_resume_and_job, generate_full_resume, generate_cover_letter, create_pdf

# # Set up OpenAI API key
# openai.api_key = st.secrets["openai_api_key"]

# st.set_page_config(page_title="AI Resume Tailor", page_icon="📄", layout="wide")
# st.title("AI Resume Tailor")

# # Initialize session state
# if 'generated' not in st.session_state:
#     st.session_state.generated = False
# if 'resume_data' not in st.session_state:
#     st.session_state.resume_data = None

# def sanitize_for_pdf(text):
#     return ''.join(char for char in text if ord(char) < 128)

# col1, col2 = st.columns(2)
# with col1:
#     resume = st.text_area("Paste your resume here", height=300)
# with col2:
#     job_description = st.text_area("Paste the job description here", height=300)

# def generate_resume():
#     if resume and job_description:
#         try:
#             with st.spinner("Analyzing and tailoring your resume..."):
#                 header, summary, comparison, education, work_experience = analyze_resume_and_job(resume, job_description)
#                 full_resume = generate_full_resume(header, summary, comparison, education, work_experience)
#                 cover_letter = generate_cover_letter(resume, job_description)
                
#                 st.session_state.resume_data = {
#                     'header': header,
#                     'summary': summary,
#                     'comparison': comparison,
#                     'education': education,
#                     'work_experience': work_experience,
#                     'full_resume': full_resume,
#                     'cover_letter': cover_letter
#                 }
#                 st.session_state.generated = True
#         except Exception as e:
#             st.error(f"An error occurred during generation: {str(e)}")
#     else:
#         st.warning("Please provide both your resume and the job description.")

# if st.button("Analyze and Tailor Resume"):
#     generate_resume()

# if st.session_state.generated:
#     data = st.session_state.resume_data
    
#     st.subheader("Tailored Header")
#     st.info(data['header'])
    
#     st.subheader("Custom Summary")
#     st.success(data['summary'])
    
#     st.subheader("Skills Comparison")
#     comp_col1, comp_col2 = st.columns(2)
#     with comp_col1:
#         st.markdown("**Your Skills & Experience**")
#         for skill in data['comparison'][0]:
#             st.write(f"• {skill}")
#     with comp_col2:
#         st.markdown("**Job Requirements**")
#         for req in data['comparison'][1]:
#             st.write(f"• {req}")
    
#     st.subheader("Education")
#     st.write(data['education'])
    
#     st.subheader("Relevant Work Experience")
#     st.write(data['work_experience'])
    
#     st.subheader("Complete Tailored Resume")
#     st.text_area("Copy and edit your tailored resume:", data['full_resume'], height=400)
#     st.info("Please review and edit the generated resume to ensure all information is accurate and fits on one page. You may need to adjust the work experience and education sections.")
    
#     st.subheader("Cover Letter")
#     st.text_area("Copy your cover letter:", data['cover_letter'], height=300)

#     # Generate PDF downloads
#     try:
#         create_pdf(sanitize_for_pdf(data['full_resume']), "tailored_resume.pdf")
#         create_pdf(sanitize_for_pdf(data['cover_letter']), "cover_letter.pdf")

#         col1, col2 = st.columns(2)
#         with col1:
#             with open("tailored_resume.pdf", "rb") as pdf_file:
#                 PDFbyte = pdf_file.read()
#             st.download_button(label="Download Resume as PDF",
#                                data=PDFbyte,
#                                file_name="tailored_resume.pdf",
#                                mime='application/octet-stream')
        
#         with col2:
#             with open("cover_letter.pdf", "rb") as pdf_file:
#                 PDFbyte = pdf_file.read()
#             st.download_button(label="Download Cover Letter as PDF",
#                                data=PDFbyte,
#                                file_name="cover_letter.pdf",
#                                mime='application/octet-stream')
#     except Exception as e:
#         st.error(f"An error occurred while creating PDFs: {str(e)}")

# if st.button("Start Over"):
#     for key in list(st.session_state.keys()):
#         del st.session_state[key]
#     st.experimental_rerun()

# st.markdown("---")
# st.markdown("Built with ❤️ using Streamlit and OpenAI GPT-4")
