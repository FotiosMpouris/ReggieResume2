import openai
import re
from fpdf import FPDF
from datetime import date
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')

def extract_keywords(job_description):
    """
    Extracts the top 20 most common keywords from the job description,
    excluding common stopwords.
    """
    # Tokenize the job description
    tokens = word_tokenize(job_description.lower())
    # Remove stopwords and non-alphabetic tokens
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in tokens if word.isalpha() and word not in stop_words]
    # Get the most common words as keywords
    common_keywords = [word for word, freq in Counter(keywords).most_common(20)]
    return common_keywords

def match_keywords(resume, job_description):
    """
    Matches extracted keywords from the job description against the resume.
    Returns lists of matched and missing keywords.
    """
    keywords = extract_keywords(job_description)
    matched_keywords = [word for word in keywords if word.lower() in resume.lower()]
    missing_keywords = [word for word in keywords if word.lower() not in resume.lower()]
    return matched_keywords, missing_keywords

def provide_ats_tips(matched_keywords, missing_keywords):
    """
    Provides ATS optimization tips based on matched and missing keywords.
    """
    tips = []
    if missing_keywords:
        tips.append("🔑 **ATS Optimization Tips:**")
        tips.append("Consider incorporating the following keywords to improve ATS compatibility:")
        for word in missing_keywords:
            tips.append(f"- {word}")
    else:
        tips.append("🎉 **Great Job!** Your resume is well-optimized for ATS.")
    return "\n".join(tips)

def analyze_resume_and_job(resume, job_description):
    """
    Analyzes the resume and job description to extract tailored sections,
    including ATS keyword matching.
    """
    system_message = """
    You are an expert resume analyst and career advisor with decades of experience in HR and recruitment across various industries. Your task is to analyze the provided resume and job description, then provide:
    1. A tailored header for the resume, including the candidate's name and key contact information.
    2. A custom summary (3-4 sentences) that highlights the candidate's most relevant skills and experiences for this specific job.
    3. A detailed comparison of the candidate's skills and the job requirements, categorized into Technical Skills, Soft Skills, Experience, and Qualifications. For each category, list at least 5 key points that match the job requirements. Provide a brief explanation for each match.
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
    **Technical Skills**
    - Skill 1: [Explanation]
    - Skill 2: [Explanation]
    - Skill 3: [Explanation]
    - Skill 4: [Explanation]
    - Skill 5: [Explanation]

    **Soft Skills**
    - Skill 1: [Explanation]
    - Skill 2: [Explanation]
    - Skill 3: [Explanation]
    - Skill 4: [Explanation]
    - Skill 5: [Explanation]

    **Experience**
    - Experience 1: [Explanation]
    - Experience 2: [Explanation]
    - Experience 3: [Explanation]
    - Experience 4: [Explanation]
    - Experience 5: [Explanation]

    **Qualifications**
    - Qualification 1: [Explanation]
    - Qualification 2: [Explanation]
    - Qualification 3: [Explanation]
    - Qualification 4: [Explanation]
    - Qualification 5: [Explanation]

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
    return process_gpt_output(output, resume, job_description)

def process_gpt_output(output, resume, job_description):
    """
    Processes the GPT output to extract different sections and perform ATS keyword matching.
    """
    sections = re.split(r'\n\n(?=HEADER:|SUMMARY:|COMPARISON:|EDUCATION:|RELEVANT WORK EXPERIENCE:|COVER LETTER INFO:)', output)
    
    header = re.sub(r'^HEADER:\s*', '', sections[0], flags=re.MULTILINE).strip()
    summary = re.sub(r'^SUMMARY:\s*', '', sections[1], flags=re.MULTILINE).strip()
    
    comparison_section = re.sub(r'^COMPARISON:\s*', '', sections[2], flags=re.MULTILINE).strip()
    # Parse each category
    technical_skills = re.findall(r'\*\*Technical Skills\*\*\n((?:- .+\n?)+)', comparison_section)
    soft_skills = re.findall(r'\*\*Soft Skills\*\*\n((?:- .+\n?)+)', comparison_section)
    experience = re.findall(r'\*\*Experience\*\*\n((?:- .+\n?)+)', comparison_section)
    qualifications = re.findall(r'\*\*Qualifications\*\*\n((?:- .+\n?)+)', comparison_section)
    
    def parse_skills(skills_raw):
        return [skill.strip() for skill in skills_raw[0].split('- ')[1:] if skill]
    
    technical_skills = parse_skills(technical_skills) if technical_skills else []
    soft_skills = parse_skills(soft_skills) if soft_skills else []
    experience = parse_skills(experience) if experience else []
    qualifications = parse_skills(qualifications) if qualifications else []
    
    education = re.sub(r'^EDUCATION:\s*', '', sections[3], flags=re.MULTILINE).strip()
    work_experience = re.sub(r'^RELEVANT WORK EXPERIENCE:\s*', '', sections[4], flags=re.MULTILINE).strip()
    
    cover_letter_info_raw = re.sub(r'^COVER LETTER INFO:\s*', '', sections[5], flags=re.MULTILINE).strip().split('\n')
    cover_letter_info = {item.split(':')[0].strip(): item.split(':')[1].strip() for item in cover_letter_info_raw}
    
    # Perform ATS keyword matching
    matched_keywords, missing_keywords = match_keywords(resume, job_description)
    ats_tips = provide_ats_tips(matched_keywords, missing_keywords)
    
    return (
        header,
        summary,
        {
            'Technical Skills': technical_skills,
            'Soft Skills': soft_skills,
            'Experience': experience,
            'Qualifications': qualifications
        },
        education,
        work_experience,
        cover_letter_info,
        ats_tips
    )

def generate_full_resume(header, summary, skills_comparison, education, work_experience, ats_tips, company_name):
    """
    Generates the full tailored resume with ATS optimization tips.
    """
    comparison = ""
    for category, items in skills_comparison.items():
        comparison += f"**{category}**\n"
        for item in items:
            comparison += f"- {item}\n"
        comparison += "\n"
    
    full_resume = f"""
{header}

SUMMARY
{summary}

COMPARISON
{comparison}

EDUCATION
{education}

RELEVANT WORK EXPERIENCE
{work_experience}

ATS TIPS
{ats_tips}
"""
    return full_resume

def generate_cover_letter(resume, job_description, cover_letter_info):
    """
    Generates a personalized cover letter based on the resume and job description.
    """
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

def generate_follow_up_paragraph(full_resume, cover_letter):
    """
    Generates a concise, friendly follow-up paragraph with minimal wit,
    tailored to complement the resume and cover letter.
    """
    system_message = """
    You are a professional writer tasked with crafting a concise, friendly follow-up paragraph that complements the provided resume and cover letter. The tone should be upbeat and witty without excessive sarcasm. If a joke is included, it should be relevant to the HR department. The paragraph should express genuine interest in the position and encourage the reader to take the next step.
    """

    user_message = f"""
    Based on the following resume and cover letter, write a short follow-up paragraph to be added to my application. Ensure it sounds like it's written by me.

    Resume:
    {full_resume}

    Cover Letter:
    {cover_letter}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    follow_up = response.choices[0].message.content.strip()
    return follow_up

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
    """
    Creates a PDF file from the provided content.
    Handles both resumes and cover letters with appropriate formatting.
    """
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
        # Existing resume PDF generation code (with modifications)
        left_margin = 20
        right_margin = 20
        top_margin = 20
        pdf.set_margins(left_margin, top_margin, right_margin)
        
        pdf.set_auto_page_break(auto=True, margin=15)  # Bottom margin
        
        # Calculate effective page width (accounting for margins)
        effective_page_width = pdf.w - left_margin - right_margin
        
        # Split content into main sections
        main_sections = re.split(r'\n\n(?=SUMMARY|COMPARISON|EDUCATION|RELEVANT WORK EXPERIENCE|ATS TIPS)', content)
        
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
            if section.startswith("COMPARISON"):
                pdf.set_font("DejaVu", 'B', 11)  # Set to bold for section headers
                # Extract each category
                categories = re.findall(r'\*\*(.*?)\*\*\n((?:- .+\n?)+)', section)
                for category, items in categories:
                    pdf.set_font("DejaVu", 'B', 11)
                    pdf.multi_cell(0, 5, f"{category}", ln=True)
                    pdf.set_font("DejaVu", '', 11)
                    for item in items.strip().split('\n'):
                        pdf.multi_cell(0, 5, item, ln=True)
                    pdf.ln(2)
            elif section.startswith("EDUCATION"):
                pdf.set_font("DejaVu", 'B', 11)  # Set to bold for section headers
                pdf.cell(0, 5, "EDUCATION", ln=True)
                pdf.set_font("DejaVu", '', 11)
                pdf.multi_cell(effective_page_width, 5, section.replace("EDUCATION:", "").strip(), align='J')
                pdf.ln(2)
            elif section.startswith("RELEVANT WORK EXPERIENCE"):
                pdf.set_font("DejaVu", 'B', 11)  # Set to bold for section headers
                pdf.cell(0, 5, "RELEVANT WORK EXPERIENCE", ln=True)
                pdf.set_font("DejaVu", '', 11)
                pdf.multi_cell(effective_page_width, 5, section.replace("RELEVANT WORK EXPERIENCE:", "").strip(), align='J')
                pdf.ln(2)
            elif section.startswith("ATS TIPS"):
                pdf.set_font("DejaVu", 'B', 11)  # Set to bold for section headers
                pdf.cell(0, 5, "ATS TIPS", ln=True)
                pdf.set_font("DejaVu", '', 11)
                pdf.multi_cell(effective_page_width, 5, section.replace("ATS TIPS:", "").strip(), align='J')
                pdf.ln(2)
            else:
                pdf.set_font("DejaVu", 'B', 11)  # Set to bold for other section headers if any
                section_header = section.split('\n')[0]
                pdf.cell(0, 5, section_header, ln=True)
                pdf.set_font("DejaVu", '', 11)
                pdf.multi_cell(effective_page_width, 5, '\n'.join(section.split('\n')[1:]).strip(), align='J')
                pdf.ln(2)
            
            if i < len(main_sections) - 1:
                pdf.ln(3)
                pdf.line(left_margin, pdf.get_y(), pdf.w - right_margin, pdf.get_y())
                pdf.ln(3)

def generate_pdf(content, filename):
    """
    Wrapper function to create a PDF.
    """
    create_pdf(content, filename)
