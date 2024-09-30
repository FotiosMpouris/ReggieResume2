import openai
import re
from fpdf import FPDF

def analyze_resume_and_job(resume, job_description):
    system_message = """
    You are an expert resume analyst and career advisor with decades of experience in HR and recruitment across various industries. Your task is to analyze the provided resume and job description, then provide:
    1. A tailored header for the resume, including the candidate's name and key contact information.
    2. A custom summary (3-4 sentences) that highlights the candidate's most relevant skills and experiences for this specific job.
    3. A detailed two-column comparison of the candidate's skills and the job requirements, listing at least 5 key points for each.
    4. Extract and summarize the candidate's education information.
    5. Extract and summarize the most relevant work experience for this job, focusing on the most recent or most applicable positions.
    """

    user_message = f"""
    Please analyze the following resume and job description:

    Resume:
    {resume}

    Job Description:
    {job_description}

    Provide your analysis in the following format:
    HEADER:
    [Tailored header here]

    SUMMARY:
    [Custom summary here]

    COMPARISON:
    [Your Skills & Experience]|[Job Requirements]
    Skill/Experience 1|Requirement 1
    Skill/Experience 2|Requirement 2
    Skill/Experience 3|Requirement 3
    Skill/Experience 4|Requirement 4
    Skill/Experience 5|Requirement 5

    EDUCATION:
    [Summarized education information]

    RELEVANT WORK EXPERIENCE:
    [Summarized relevant work experience]
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    output = response.choices[0].message.content
    return process_gpt_output(output)

def process_gpt_output(output):
    sections = re.split(r'\n\n(?=HEADER:|SUMMARY:|COMPARISON:|EDUCATION:|RELEVANT WORK EXPERIENCE:)', output)
    
    header = re.sub(r'^HEADER:\s*', '', sections[0], flags=re.MULTILINE).strip()
    summary = re.sub(r'^SUMMARY:\s*', '', sections[1], flags=re.MULTILINE).strip()
    
    comparison_raw = re.sub(r'^COMPARISON:\s*', '', sections[2], flags=re.MULTILINE).strip().split('\n')
    your_skills = [item.split('|')[0].strip() for item in comparison_raw if '|' in item]
    job_requirements = [item.split('|')[1].strip() for item in comparison_raw if '|' in item]
    
    education = re.sub(r'^EDUCATION:\s*', '', sections[3], flags=re.MULTILINE).strip()
    work_experience = re.sub(r'^RELEVANT WORK EXPERIENCE:\s*', '', sections[4], flags=re.MULTILINE).strip()
    
    return header, summary, (your_skills, job_requirements), education, work_experience

def generate_full_resume(header, summary, skills_comparison, education, work_experience):
    skills, requirements = skills_comparison
    comparison = "\n".join([f"{skill:<50} | {req}" for skill, req in zip(skills, requirements)])
    
    full_resume = f"""
{header}

SUMMARY
{summary}

SKILLS & EXPERIENCE                                 | JOB REQUIREMENTS
{comparison}

EDUCATION
{education}

RELEVANT WORK EXPERIENCE
{work_experience}
"""
    return full_resume

# New function for generating a cover letter
def generate_cover_letter(resume, job_description):
    system_message = """
    You are an expert cover letter writer with years of experience in HR and recruitment. Your task is to create a compelling, personalized cover letter based on the candidate's resume and the job description provided. The cover letter should:
    1. Be professionally formatted with appropriate salutations and closings
    2. Highlight the candidate's most relevant skills and experiences for the specific job
    3. Show enthusiasm for the position and company
    4. Be concise, typically not exceeding one page
    5. Encourage the employer to review the attached resume and consider the candidate for an interview
    """

    user_message = f"""
    Please write a cover letter based on the following resume and job description:

    Resume:
    {resume}

    Job Description:
    {job_description}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    return response.choices[0].message.content



class PDF(FPDF):
    def header(self):
        # No header for resume
        pass

    def footer(self):
        # No footer for resume
        pass
def create_pdf(content, filename):
    pdf = PDF(format='Letter')
    pdf.add_page()
    
    # Set margins (left, top, right) in millimeters
    pdf.set_margins(25, 20, 20)
    
    pdf.set_auto_page_break(auto=True, margin=20)  # Bottom margin
    
    # Calculate effective page width (accounting for margins)
    effective_page_width = pdf.w - pdf.l_margin - pdf.r_margin
    
    # Split content into sections
    sections = content.split('\n\n')
    
    # Process the first section (name, telephone, address, email)
    # Center align and make it slightly larger
    pdf.set_font("Helvetica", 'B', size=12)
    first_section_lines = sections[0].split('\n')
    for line in first_section_lines:
        pdf.cell(effective_page_width, 6, line, align='C', ln=True)
    
    # Add extra spacing after the first section
    pdf.ln(10)  # You can adjust this value to increase or decrease the space
    
    # Add a line after the first section
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(3)  # Add some space after the line
    
    # Process the rest of the sections
    pdf.set_font("Helvetica", size=11)
    for i, section in enumerate(sections[1:], 1):  # Start from the second section
        if "SKILLS & EXPERIENCE" in section:
            # Use a smaller font size for the comparison section
            pdf.set_font("Helvetica", size=6)
            
            # Split the section into lines
            lines = section.split('\n')
            
            # Write the header
            pdf.cell(effective_page_width, 4, lines[0], ln=True)
            pdf.ln(1)
            
            # Write the comparison lines
            for line in lines[1:]:
                if '|' in line:
                    left, right = line.split('|')
                    pdf.cell(effective_page_width/2, 3, left.strip(), border='L', ln=0)
                    pdf.cell(effective_page_width/2, 3, right.strip(), border='R', ln=1)
                else:
                    pdf.cell(effective_page_width, 3, line, ln=True)
            
            # Reset font size
            pdf.set_font("Helvetica", size=11)
        else:
            # Justify text for other sections
            pdf.multi_cell(effective_page_width, 5, section, align='J')
        
        # Add a line after each section except the last one
        if i < len(sections) - 1:
            pdf.ln(3)  # Add some space before the line
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(3)  # Add some space after the line

    pdf.output(filename)
# def create_pdf(content, filename):
#     pdf = PDF(format='Letter')
#     pdf.add_page()
    
#     # Set margins (left, top, right) in millimeters
#     pdf.set_margins(25, 20, 20)
    
#     pdf.set_auto_page_break(auto=True, margin=20)  # Bottom margin
    
#     # Calculate effective page width (accounting for margins)
#     effective_page_width = pdf.w - pdf.l_margin - pdf.r_margin
    
#     # Split content into sections
#     sections = content.split('\n\n')
    
#     # Process the first section (name, telephone, address, email)
#     # Center align and make it slightly larger
#     pdf.set_font("Helvetica", 'B', size=12)
#     first_section_lines = sections[0].split('\n')
#     for line in first_section_lines:
#         pdf.cell(effective_page_width, 6, line, align='C', ln=True)
    
#     # Add extra spacing after the first section
#     pdf.ln(10)  # You can adjust this value to increase or decrease the space
    
#     # Add a line after the first section
#     pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
#     pdf.ln(3)  # Add some space after the line
    
#     # Process the rest of the sections
#     pdf.set_font("Helvetica", size=11)
#     for i, section in enumerate(sections[1:], 1):  # Start from the second section
#         # Justify text
#         pdf.multi_cell(effective_page_width, 5, section, align='J')
        
#         # Add a line after each section except the last one
#         if i < len(sections) - 1:
#             pdf.ln(3)  # Add some space before the line
#             pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
#             pdf.ln(3)  # Add some space after the line

#     pdf.output(filename)
