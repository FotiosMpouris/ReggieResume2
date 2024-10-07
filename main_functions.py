import openai
import re
from fpdf import FPDF
from datetime import date

def analyze_resume_and_job(resume, job_description):
    system_message = """
    You are an expert resume analyst and career advisor with decades of experience in HR and recruitment across various industries. Your task is to analyze the provided resume and job description, then provide:
    1. A tailored header for the resume, including the candidate's name and key contact information.
    2. A custom summary (3-4 sentences) that highlights the candidate's most relevant skills and experiences for this specific job.
    3. A detailed two-column comparison of the candidate's skills and the job requirements, listing at least 6 key points for each. Include the company name from the job description before "Job Requirements".
    4. Extract and summarize the candidate's education information.
    5. Extract and summarize at least three relevant work experiences for this job, focusing on the most recent or most applicable positions. Each experience should be described in detail.
    6. Extract the full name, address, email, and phone number for use in a cover letter.
    7. Extract the company name from the job description for use in the cover letter greeting.
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
    [Your Skills & Experience]|[Company Name Job Requirements]
    Skill/Experience 1|Requirement 1
    Skill/Experience 2|Requirement 2
    Skill/Experience 3|Requirement 3
    Skill/Experience 4|Requirement 4
    Skill/Experience 5|Requirement 5

    EDUCATION:
    [Summarized education information]

    RELEVANT WORK EXPERIENCE:
    [Summarized relevant work experience 1]

    [Summarized relevant work experience 2]

    [Summarized relevant work experience 3]

    COVER LETTER INFO:
    Full Name: [Extracted full name]
    Address: [Extracted address]
    Email: [Extracted email]
    Phone: [Extracted phone number]
    Company Name: [Extracted company name]
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
    sections = re.split(r'\n\n(?=HEADER:|SUMMARY:|COMPARISON:|EDUCATION:|RELEVANT WORK EXPERIENCE:|COVER LETTER INFO:)', output)
    
    header = re.sub(r'^HEADER:\s*', '', sections[0], flags=re.MULTILINE).strip()
    summary = re.sub(r'^SUMMARY:\s*', '', sections[1], flags=re.MULTILINE).strip()
    
    comparison_raw = re.sub(r'^COMPARISON:\s*', '', sections[2], flags=re.MULTILINE).strip().split('\n')
    your_skills = [item.split('|')[0].strip() for item in comparison_raw if '|' in item]
    job_requirements = [item.split('|')[1].strip() for item in comparison_raw if '|' in item]
    
    education = re.sub(r'^EDUCATION:\s*', '', sections[3], flags=re.MULTILINE).strip()
    work_experience = re.sub(r'^RELEVANT WORK EXPERIENCE:\s*', '', sections[4], flags=re.MULTILINE).strip()
    
    cover_letter_info_raw = re.sub(r'^COVER LETTER INFO:\s*', '', sections[5], flags=re.MULTILINE).strip().split('\n')
    cover_letter_info = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in cover_letter_info_raw}
    
    return header, summary, (your_skills, job_requirements), education, work_experience, cover_letter_info

def generate_full_resume(header, summary, skills_comparison, education, work_experience, company_name):
    skills, requirements = skills_comparison
    first_name = header.split()[0]  # Assuming the first word in the header is the first name
    comparison = "\n".join([f"{skill:<50} | {req}" for skill, req in zip(skills, requirements)])
    
    full_resume = f"""
{header}

SUMMARY
{summary}

{company_name} JOB REQUIREMENTS                     | {first_name}'s MATCHING SKILLS
{comparison}

EDUCATION
{education}

RELEVANT WORK EXPERIENCE
{work_experience}
"""
    return full_resume
    
# def generate_full_resume(header, summary, skills_comparison, education, work_experience, company_name):
#     skills, requirements = skills_comparison
#     comparison = "\n".join([f"{skill:<50} | {req}" for skill, req in zip(skills, requirements)])
    
#     full_resume = f"""
# {header}

# SUMMARY
# {summary}

# SKILLS & EXPERIENCE                                 | {company_name} JOB REQUIREMENTS
# {comparison}

# EDUCATION
# {education}

# RELEVANT WORK EXPERIENCE
# {work_experience}
# """
#     return full_resume

def generate_cover_letter(resume, job_description, cover_letter_info):
    today = date.today().strftime("%B %d, %Y")
    
    system_message = """
    You are an expert cover letter writer with years of experience in HR and recruitment. Your task is to create a compelling, personalized cover letter based on the candidate's resume, the job description provided, and the specific candidate information given. The cover letter should:
    1. Highlight the candidate's most relevant skills and experiences for the specific job
    2. Show enthusiasm for the position and company
    3. Be concise, typically not exceeding one page
    4. Encourage the employer to review the attached resume and consider the candidate for an interview
    5. Do not include any salutation, contact information, or closing in the body of the letter
    """

    user_message = f"""
    Please write a cover letter based on the following information:

    Candidate Information:
    Full Name: {cover_letter_info['Full Name']}
    Company: {cover_letter_info['Company Name']}

    Resume:
    {resume}

    Job Description:
    {job_description}

    Provide only the body of the cover letter, without any salutation or closing.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    cover_letter_content = response.choices[0].message.content
    
    # Format the cover letter with the correct header, date, and salutation
    formatted_cover_letter = f"{cover_letter_info['Full Name']}\n{cover_letter_info['Address']}\n{cover_letter_info['Phone']}\n{cover_letter_info['Email']}\n\n{today}\n\nDear {cover_letter_info['Company Name']} Hiring Team,\n\n{cover_letter_content}\n\nSincerely,\n{cover_letter_info['Full Name']}"
    
    return formatted_cover_letter

class PDF(FPDF):
    def header(self):
        # No header for resume
        pass

    def footer(self):
        # No footer for resume
        pass

    def multi_cell_aligned(self, w, h, txt, border=0, align='J', fill=False, ln=1):
        # Custom method to create a multi-cell with specified alignment
        self.multi_cell(w, h, txt, border, align, fill)
        if ln == 1:
            self.ln(h)
        elif ln == 2:
            self.ln(2*h)

def create_pdf(content, filename):
    pdf = PDF(format='Letter')
    pdf.add_page()
    
    # Add Unicode fonts (regular and bold)
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
    
    if filename == "cover_letter.pdf":
        # Cover letter specific formatting
        left_margin = 25.4  # 1 inch
        right_margin = 25.4  # 1 inch
        top_margin = 25.4  # 1 inch
        pdf.set_margins(left_margin, top_margin, right_margin)
        
        pdf.set_auto_page_break(auto=True, margin=25.4)  # 1 inch bottom margin
        
        # Calculate effective page width (accounting for margins)
        effective_page_width = pdf.w - left_margin - right_margin
        
        # Set font for body text
        pdf.set_font("DejaVu", '', 11)
        
        # Split cover letter into paragraphs
        paragraphs = content.split('\n\n')
        
        # Process contact information
        contact_info = paragraphs[0].split('\n')
        for line in contact_info:
            pdf.set_x(left_margin)  # Ensure consistent left alignment
            pdf.cell(0, 5, line.strip(), ln=True, align='L')
        pdf.ln(5)
        
        # contact_info = paragraphs[0].split('\n')
        # for line in contact_info:
        #     pdf.cell(0, 5, line.strip(), ln=True)
        # pdf.ln(5)
        
        # Process date and salutation
        if len(paragraphs) > 1:
            date_salutation = paragraphs[1].split('\n')
            if len(date_salutation) >= 2:
                # Date on the right
                pdf.cell(effective_page_width, 5, date_salutation[0].strip(), align='R', ln=True)
                pdf.ln(5)
                # Salutation on the left
                pdf.cell(0, 5, date_salutation[1].strip(), ln=True)
            pdf.ln(5)
        
        # Process the body of the letter
        for paragraph in paragraphs[2:]:
            pdf.multi_cell(effective_page_width, 5, paragraph.strip(), align='J')
            pdf.ln(5)
               
    else:
        # Existing resume PDF generation code
        left_margin = 20
        right_margin = 20
        top_margin = 20
        pdf.set_margins(left_margin, top_margin, right_margin)
        
        pdf.set_auto_page_break(auto=True, margin=15)  # Bottom margin
        
        # Calculate effective page width (accounting for margins)
        effective_page_width = pdf.w - left_margin - right_margin
        
        # Split content into main sections
        main_sections = re.split(r'\n\n(?=SUMMARY|SKILLS & EXPERIENCE|EDUCATION|RELEVANT WORK EXPERIENCE)', content)
        
        # Process the header section (name, telephone, address, email)
        pdf.set_font("DejaVu", 'B', 12)  # Set to bold, slightly larger than body text
        header_lines = main_sections[0].split('\n')
        header_info = "  ".join([line.split(": ", 1)[-1] for line in header_lines])
        
        # Extract first name from the header
        first_name = header_info.split()[0]
        
        # Center the header between left and right margins
        header_width = pdf.get_string_width(header_info)
        if header_width > effective_page_width:
            # If header is too wide, reduce font size
            font_size = 12
            while header_width > effective_page_width and font_size > 9:
                font_size -= 0.5
                pdf.set_font("DejaVu", 'B', font_size)  # Keep bold
                header_width = pdf.get_string_width(header_info)
        
        # Calculate the center position and shift it slightly to the left
        x_position = (pdf.w - header_width) / 2 - pdf.get_string_width("  ")
        pdf.set_x(x_position)
        
        pdf.cell(header_width, 6, header_info, align='C', ln=True)
        
        # Add extra spacing after the header
        pdf.ln(10)
        
        # Add a line after the header
        pdf.line(left_margin, pdf.get_y(), pdf.w - right_margin, pdf.get_y())
        pdf.ln(3)
        
        # Process the rest of the sections
        pdf.set_font("DejaVu", '', 11)
                       
        for i, section in enumerate(main_sections[1:], 1):
            if section.startswith("SKILLS & EXPERIENCE"):
                pdf.set_font("DejaVu", 'B', 11)  # Set to bold for section headers
                col_width = effective_page_width / 2
                
                # Extract company name and job requirements header
                company_job_req = section.split('\n')[0].split('|')[1].strip()
                
                # Write both headers on the same line with personalization (swapped order)
                pdf.cell(col_width, 5, company_job_req, align='L', border=0)
                pdf.cell(col_width, 5, f"{first_name}'s Skills & Experience", align='L', border=0, ln=True)
                pdf.ln(2)
                
                pdf.set_font("DejaVu", '', 11)  # Reset to regular font
                
                lines = section.split('\n')[1:]  # Skip the header line
                
                max_y = pdf.get_y()
                first_item = True
                for line in lines:
                    if '|' in line:
                        left, right = line.split('|')
                        if first_item:
                            first_item = False
                            continue  # Skip the first item as it's redundant
                        pdf.set_xy(left_margin, max_y)
                        pdf.multi_cell(col_width - 2, 5, "• " + right.strip(), align='L')  # Job Requirements (left column)
                        new_y = pdf.get_y()
                        
                        pdf.set_xy(left_margin + col_width, max_y)
                        pdf.multi_cell(col_width - 2, 5, "• " + left.strip(), align='L')  # Your Skills & Experience (right column)
                        
                        max_y = max(new_y, pdf.get_y()) + 2  # Add some space between items
                    else:
                        pdf.set_xy(left_margin, max_y)
                        pdf.multi_cell(effective_page_width - 2, 5, line, align='L')
                        max_y = pdf.get_y() + 2
                
                pdf.set_y(max_y)
            else:
                pdf.set_font("DejaVu", 'B', 11)  # Set to bold for section headers
                pdf.cell(0, 5, section.split('\n')[0], ln=True)  # Write section header
                pdf.set_font("DejaVu", '', 11)  # Reset to regular font
                pdf.multi_cell(effective_page_width, 5, '\n'.join(section.split('\n')[1:]), align='J')
            
            if i < len(main_sections) - 1:
                pdf.ln(3)
                pdf.line(left_margin, pdf.get_y(), pdf.w - right_margin, pdf.get_y())
                pdf.ln(3)
    
    pdf.output(filename)
    
    #     left_margin = 20
    #     right_margin = 20
    #     top_margin = 20
    #     pdf.set_margins(left_margin, top_margin, right_margin)
        
    #     pdf.set_auto_page_break(auto=True, margin=15)  # Bottom margin
        
    #     # Calculate effective page width (accounting for margins)
    #     effective_page_width = pdf.w - left_margin - right_margin
        
    #     # Split content into main sections
    #     main_sections = re.split(r'\n\n(?=SUMMARY|SKILLS & EXPERIENCE|EDUCATION|RELEVANT WORK EXPERIENCE)', content)
        
    #     # Process the header section (name, telephone, address, email)
    #     pdf.set_font("DejaVu", 'B', 12)  # Set to bold, slightly larger than body text
    #     header_lines = main_sections[0].split('\n')
    #     header_info = "  ".join([line.split(": ", 1)[-1] for line in header_lines])
        
    #     # Extract first name from the header
    #     first_name = header_info.split()[0]
        
    #     # Center the header between left and right margins
    #     header_width = pdf.get_string_width(header_info)
    #     if header_width > effective_page_width:
    #         # If header is too wide, reduce font size
    #         font_size = 12
    #         while header_width > effective_page_width and font_size > 9:
    #             font_size -= 0.5
    #             pdf.set_font("DejaVu", 'B', font_size)  # Keep bold
    #             header_width = pdf.get_string_width(header_info)
        
    #     # Calculate the center position and shift it slightly to the left
    #     x_position = (pdf.w - header_width) / 2 - pdf.get_string_width("  ")
    #     pdf.set_x(x_position)
        
    #     pdf.cell(header_width, 6, header_info, align='C', ln=True)
        
    #     # Add extra spacing after the header
    #     pdf.ln(10)
        
    #     # Add a line after the header
    #     pdf.line(left_margin, pdf.get_y(), pdf.w - right_margin, pdf.get_y())
    #     pdf.ln(3)
        
    #     # Process the rest of the sections
    #     pdf.set_font("DejaVu", '', 11)
    #     for i, section in enumerate(main_sections[1:], 1):
    #         if section.startswith("SKILLS & EXPERIENCE"):
    #             pdf.set_font("DejaVu", 'B', 11)  # Set to bold for section headers
    #             col_width = effective_page_width / 2
                
    #             # Extract company name and job requirements header
    #             company_job_req = section.split('\n')[0].split('|')[1].strip()
                
    #             # Write both headers on the same line with personalization
    #             pdf.cell(col_width, 5, f"{first_name}'s Skills & Experience", align='L', border=0)
    #             pdf.cell(col_width, 5, company_job_req, align='L', border=0, ln=True)
    #             pdf.ln(2)
                
    #             pdf.set_font("DejaVu", '', 11)  # Reset to regular font
                
    #             lines = section.split('\n')[1:]  # Skip the header line
                
    #             max_y = pdf.get_y()
    #             first_item = True
    #             for line in lines:
    #                 if '|' in line:
    #                     left, right = line.split('|')
    #                     if first_item:
    #                         first_item = False
    #                         continue  # Skip the first item as it's redundant
    #                     pdf.set_xy(left_margin, max_y)
    #                     pdf.multi_cell(col_width - 2, 5, "• " + left.strip(), align='L')  # Unicode bullet point
    #                     new_y = pdf.get_y()
                        
    #                     pdf.set_xy(left_margin + col_width, max_y)
    #                     pdf.multi_cell(col_width - 2, 5, "• " + right.strip(), align='L')  # Unicode bullet point
                        
    #                     max_y = max(new_y, pdf.get_y()) + 2  # Add some space between items
    #                 else:
    #                     pdf.set_xy(left_margin, max_y)
    #                     pdf.multi_cell(effective_page_width - 2, 5, line, align='L')
    #                     max_y = pdf.get_y() + 2
                
    #             pdf.set_y(max_y)
    #         else:
    #             pdf.set_font("DejaVu", 'B', 11)  # Set to bold for section headers
    #             pdf.cell(0, 5, section.split('\n')[0], ln=True)  # Write section header
    #             pdf.set_font("DejaVu", '', 11)  # Reset to regular font
    #             pdf.multi_cell(effective_page_width, 5, '\n'.join(section.split('\n')[1:]), align='J')
            
    #         if i < len(main_sections) - 1:
    #             pdf.ln(3)
    #             pdf.line(left_margin, pdf.get_y(), pdf.w - right_margin, pdf.get_y())
    #             pdf.ln(3)
    
    # pdf.output(filename)
