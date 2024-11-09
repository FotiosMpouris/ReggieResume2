import openai
import re
from fpdf import FPDF
from datetime import date
import spacy
import os

# Load spaCy English model for keyword extraction
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If the model isn't found, inform the user to install it
    raise OSError(
        "SpaCy model 'en_core_web_sm' not found. "
        "Please ensure it's installed by adding 'en_core_web_sm==3.6.4' to your requirements.txt."
    )

def extract_keywords(job_description, num_keywords=15):
    """
    Extracts the top keywords from the job description using spaCy's NLP capabilities.
    """
    doc = nlp(job_description.lower())
    # Filter tokens: nouns, proper nouns, verbs, adjectives
    keywords = [
        token.text
        for token in doc
        if token.is_alpha and not token.is_stop and token.pos_ in ['NOUN', 'PROPN', 'VERB', 'ADJ']
    ]
    # Frequency distribution
    freq = {}
    for word in keywords:
        freq[word] = freq.get(word, 0) + 1
    # Sort and get top keywords
    sorted_keywords = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    top_keywords = [word for word, count in sorted_keywords[:num_keywords]]
    return top_keywords

def analyze_resume_and_job(resume, job_description):
    """
    Analyzes the resume and job description, extracting tailored information and optimizing for ATS.
    """
    system_message = """
    You are an expert resume analyst and career advisor with decades of experience in HR and recruitment across various industries. 
    Your task is to analyze the provided resume and job description, then provide:
    1. A tailored header for the resume, including the candidate's name and key contact information.
    2. A custom summary (3-4 sentences) that highlights the candidate's most relevant skills and experiences for this specific job.
    3. A detailed two-column comparison of the candidate's skills and the job requirements, listing at least 7 key points for each. Ensure candidate's skills comparison is comparable to Job Requirements, and write candidate's skill in a sentence to best match Job Requirements statement. Include the company name from the job description before "Job Requirements".
    4. Extract and summarize the candidate's education information.
    5. Extract and summarize at least three relevant work experiences for this job, focusing on the most recent or most applicable positions. Each experience should be described in detail.
    6. Extract the full name, address, email, and phone number for use in a cover letter.
    7. Extract the company name from the job description for use in the cover letter greeting.
    8. Extract key skills and keywords from the job description for ATS optimization.
    """

    # Extract keywords for ATS
    keywords = extract_keywords(job_description)
    keyword_str = ', '.join(keywords)

    user_message = f"""
    Please analyze the following resume and job description with a focus on keyword optimization for ATS:

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
    Skill/Experience 6|Requirement 6
    Skill/Experience 7|Requirement 7

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

    ATS KEYWORDS:
    {keyword_str}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3
        )
        output = response.choices[0].message.content
        return process_gpt_output(output)
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None

def process_gpt_output(output):
    """
    Processes the GPT-4 output and extracts relevant sections.
    """
    sections = re.split(
        r'\n\n(?=HEADER:|SUMMARY:|COMPARISON:|EDUCATION:|RELEVANT WORK EXPERIENCE:|COVER LETTER INFO:|ATS KEYWORDS:)', 
        output
    )

    try:
        header = re.sub(r'^HEADER:\s*', '', sections[0], flags=re.MULTILINE).strip()
        summary = re.sub(r'^SUMMARY:\s*', '', sections[1], flags=re.MULTILINE).strip()

        comparison_raw = re.sub(r'^COMPARISON:\s*', '', sections[2], flags=re.MULTILINE).strip().split('\n')
        your_skills = [item.split('|')[0].strip() for item in comparison_raw if '|' in item]
        job_requirements = [item.split('|')[1].strip() for item in comparison_raw if '|' in item]

        education = re.sub(r'^EDUCATION:\s*', '', sections[3], flags=re.MULTILINE).strip()
        work_experience = re.sub(r'^RELEVANT WORK EXPERIENCE:\s*', '', sections[4], flags=re.MULTILINE).strip()

        cover_letter_info_raw = re.sub(r'^COVER LETTER INFO:\s*', '', sections[5], flags=re.MULTILINE).strip().split('\n')
        cover_letter_info = {
            item.split(':', 1)[0].strip(): item.split(':', 1)[1].strip()
            for item in cover_letter_info_raw if ':' in item
        }

        ats_keywords = re.sub(r'^ATS KEYWORDS:\s*', '', sections[6], flags=re.MULTILINE).strip().split(', ')

        return header, summary, (your_skills, job_requirements), education, work_experience, cover_letter_info, ats_keywords
    except IndexError as e:
        print(f"Error processing GPT output: {e}")
        return None

def generate_full_resume(header, summary, skills_comparison, education, work_experience, company_name):
    """
    Generates the full resume text with proper formatting.
    """
    skills, requirements = skills_comparison
    comparison = "\n".join([f"{skill:<50} | {req}" for skill, req in zip(skills, requirements)])

    full_resume = f"""
{header}

SUMMARY
{summary}

SKILLS & EXPERIENCE                                 | {company_name} JOB REQUIREMENTS
{comparison}

EDUCATION
{education}

RELEVANT WORK EXPERIENCE
{work_experience}
    """
    return full_resume.strip()

def generate_cover_letter(resume, job_description, cover_letter_info, tone='professional'):
    """
    Generates a cover letter based on the resume, job description, and desired tone.
    """
    today = date.today().strftime("%B %d, %Y")

    system_message = f"""
    You are an expert cover letter writer with years of experience in HR and recruitment. 
    Your task is to create a compelling, personalized cover letter based on the candidate's resume, the job description provided, and the specific candidate information given. 
    The cover letter should:
    1. Highlight the candidate's most relevant skills and experiences for the specific job
    2. Show enthusiasm for the position and company
    3. Be concise, typically not exceeding one page
    4. Encourage the employer to review the attached resume and consider the candidate for an interview
    5. Adjust the tone to be {tone}.
    6. Do not include any salutation, contact information, or closing in the body of the letter
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

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5
        )

        cover_letter_content = response.choices[0].message.content

        # Format the cover letter with the correct header, date, and salutation
        formatted_cover_letter = f"""{cover_letter_info['Full Name']}
{cover_letter_info['Address']}
{cover_letter_info['Phone']}
{cover_letter_info['Email']}

{today}

Dear {cover_letter_info['Company Name']} Hiring Team,

{cover_letter_content}

Sincerely,
{cover_letter_info['Full Name']}
"""

        return formatted_cover_letter
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None

def generate_follow_up_message(resume, job_description, cover_letter_info, custom_message=None):
    """
    Generates a follow-up message based on the resume, job description, and user customization.
    """
    system_message = """
    You are an expert career advisor specialized in crafting effective follow-up messages after job applications. 
    Your task is to create a professional and concise follow-up message based on the candidate's resume, 
    the job description, and any customization provided by the user.
    """

    if custom_message:
        custom = f"Custom Message (if any):\n{custom_message}"
    else:
        custom = "Custom Message (if any):\nI am writing to follow up on my application for the [Job Title] position. I am very enthusiastic about the opportunity to contribute to [Company Name] and would like to inquire about the status of my application."

    user_prompt = f"""
    Candidate Information:
    Full Name: {cover_letter_info['Full Name']}
    Company: {cover_letter_info['Company Name']}

    Resume:
    {resume}

    Job Description:
    {job_description}

    {custom}

    Please generate a professional follow-up message.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        follow_up_content = response.choices[0].message.content
        return follow_up_content
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None

class PDF(FPDF):
    def header(self):
        # Override to disable default header
        pass

    def footer(self):
        # Override to disable default footer
        pass

    def multi_cell_aligned(self, w, h, txt, border=0, align='J', fill=False, ln=1):
        """
        Custom method to create a multi-cell with specified alignment.
        """
        self.multi_cell(w, h, txt, border, align, fill)
        if ln == 1:
            self.ln(h)
        elif ln == 2:
            self.ln(2*h)

def create_pdf(content, filename):
    """
    Creates a PDF file (resume, cover letter, or follow-up message) with enhanced formatting.
    """
    pdf = PDF(format='Letter')
    pdf.add_page()

    # Define the path to the fonts directory
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')

    # Verify that font files exist
    regular_font_path = os.path.join(fonts_dir, 'DejaVuSansCondensed.ttf')
    bold_font_path = os.path.join(fonts_dir, 'DejaVuSansCondensed-Bold.ttf')

    if not os.path.isfile(regular_font_path) or not os.path.isfile(bold_font_path):
        raise FileNotFoundError(
            "Font files not found. Please ensure 'DejaVuSansCondensed.ttf' and "
            "'DejaVuSansCondensed-Bold.ttf' are present in the 'fonts' directory."
        )

    # Add Unicode fonts (regular and bold)
    pdf.add_font('DejaVu', '', regular_font_path, uni=True)
    pdf.add_font('DejaVu', 'B', bold_font_path, uni=True)

    if filename.lower() in ["cover_letter.pdf", "follow_up_message.pdf"]:
        # Cover letter and Follow-Up message specific formatting
        left_margin = 25.4  # 1 inch
        right_margin = 25.4  # 1 inch
        top_margin = 25.4  # 1 inch
        pdf.set_margins(left_margin, top_margin, right_margin)

        pdf.set_auto_page_break(auto=True, margin=25.4)  # 1 inch bottom margin

        # Calculate effective page width (accounting for margins)
        effective_page_width = pdf.w - left_margin - right_margin

        # Set font for body text
        pdf.set_font("DejaVu", '', 11)

        # Split content into paragraphs
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
        # Resume specific formatting
        left_margin = 20
        right_margin = 20
        top_margin = 20
        pdf.set_margins(left_margin, top_margin, right_margin)

        pdf.set_auto_page_break(auto=True, margin=15)  # Bottom margin

        # Calculate effective page width (accounting for margins)
        effective_page_width = pdf.w - left_margin - right_margin

        # Split content into main sections
        main_sections = re.split(
            r'\n\n(?=SUMMARY|SKILLS & EXPERIENCE|EDUCATION|RELEVANT WORK EXPERIENCE)', 
            content
        )

        # Process the header section (name, telephone, address, email)
        pdf.set_font("DejaVu", 'B', 16)  # Set to bold, larger font for the name
        header_lines = main_sections[0].split('\n')
        header_info = "  ".join([
            line.split(": ", 1)[-1] for line in header_lines 
            if ": " in line
        ])

        # Center the header
        pdf.cell(0, 10, header_info, ln=True, align='C')

        # Add extra spacing after the header
        pdf.ln(5)

        # Add a line after the header
        pdf.set_line_width(0.5)
        pdf.line(left_margin, pdf.get_y(), pdf.w - right_margin, pdf.get_y())
        pdf.ln(10)

        # Process the rest of the sections
        for section in main_sections[1:]:
            if section.startswith("SKILLS & EXPERIENCE"):
                pdf.set_font("DejaVu", 'B', 12)  # Bold for section headers
                pdf.cell(0, 10, "SKILLS & EXPERIENCE", ln=True)
                pdf.set_font("DejaVu", '', 11)  # Regular font for content
                pdf.multi_cell(effective_page_width, 7, section.replace("SKILLS & EXPERIENCE", "").strip(), align='L')
            elif section.startswith("SUMMARY"):
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(0, 10, "SUMMARY", ln=True)
                pdf.set_font("DejaVu", '', 11)
                pdf.multi_cell(effective_page_width, 7, section.replace("SUMMARY", "").strip(), align='J')
            elif section.startswith("EDUCATION"):
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(0, 10, "EDUCATION", ln=True)
                pdf.set_font("DejaVu", '', 11)
                pdf.multi_cell(effective_page_width, 7, section.replace("EDUCATION", "").strip(), align='L')
            elif section.startswith("RELEVANT WORK EXPERIENCE"):
                pdf.set_font("DejaVu", 'B', 12)
                pdf.cell(0, 10, "RELEVANT WORK EXPERIENCE", ln=True)
                pdf.set_font("DejaVu", '', 11)
                pdf.multi_cell(effective_page_width, 7, section.replace("RELEVANT WORK EXPERIENCE", "").strip(), align='L')
            pdf.ln(5)
        
    pdf.output(filename)

# Example usage (for testing purposes)
if __name__ == "__main__":
    # Example resume and job description
    example_resume = """
Full Name: John Doe
Address: 123 Main Street, Anytown, USA
Email: johndoe@example.com
Phone: (123) 456-7890

SUMMARY
Experienced software engineer with a strong background in developing scalable web applications and working with cross-functional teams.

SKILLS & EXPERIENCE
- Proficient in Python, JavaScript, and Java
- Experienced with Django, React, and Node.js
- Strong understanding of RESTful APIs and microservices architecture
- Excellent problem-solving and debugging skills
- Familiar with AWS and cloud deployment
- Agile and Scrum methodologies
- Version control using Git

EDUCATION
Bachelor of Science in Computer Science, University of Technology, 2018

RELEVANT WORK EXPERIENCE
Senior Software Engineer at Tech Solutions (2020 - Present)
- Led a team of 5 engineers in developing a scalable e-commerce platform.
- Implemented RESTful APIs, improving system performance by 30%.

Software Engineer at Web Innovators (2018 - 2020)
- Developed front-end components using React, enhancing user experience.
- Collaborated with back-end developers to integrate APIs.
"""

    example_job_description = """
We are seeking a highly skilled Software Engineer to join our dynamic team at Innovative Tech Corp. The ideal candidate will have experience in developing scalable web applications, a strong understanding of microservices architecture, and proficiency in Python and JavaScript. Responsibilities include designing and implementing RESTful APIs, collaborating with cross-functional teams, and deploying applications on AWS. Familiarity with Agile methodologies and version control systems is essential.
"""

    # Analyze resume and job description
    analysis = analyze_resume_and_job(example_resume, example_job_description)
    if analysis:
        header, summary, skills_comparison, education, work_experience, cover_letter_info, ats_keywords = analysis

        # Generate full resume
        full_resume = generate_full_resume(header, summary, skills_comparison, education, work_experience, cover_letter_info['Company Name'])
        print("Full Resume:\n", full_resume)

        # Generate cover letter with selected tone
        cover_letter = generate_cover_letter(full_resume, example_job_description, cover_letter_info, tone='confident')
        print("\nCover Letter:\n", cover_letter)

        # Generate follow-up message
        follow_up = generate_follow_up_message(example_resume, example_job_description, cover_letter_info)
        print("\nFollow-Up Message:\n", follow_up)

        # Create PDFs
        create_pdf(full_resume, "resume.pdf")
        create_pdf(cover_letter, "cover_letter.pdf")
        create_pdf(follow_up, "follow_up_message.pdf")
