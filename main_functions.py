import openai
import re

def analyze_resume_and_job(resume, job_description):
    system_message = """
    You are an expert resume analyst and career advisor with decades of experience in HR and recruitment across various industries. Your skills include:
    
    1. Deep understanding of job market trends and industry-specific requirements
    2. Ability to extract key skills and experiences from resumes and job descriptions
    3. Talent for identifying transferable skills and making connections between seemingly unrelated experiences
    4. Exceptional writing skills, allowing you to craft compelling summaries and headers
    5. Strong analytical capabilities to compare and contrast candidate qualifications with job requirements
    6. Knack for highlighting a candidate's unique value proposition
    7. Sensitivity to diversity and inclusion in the hiring process
    
    Your task is to carefully analyze the provided resume and job description. Then, you will:
    1. Create a tailored header for the resume, including the candidate's name and key contact information.
    2. Write a custom summary (3-4 sentences) that compellingly highlights the candidate's most relevant skills and experiences for this specific job.
    3. Create a detailed two-column comparison of the candidate's skills and the job requirements, listing at least 5 key points for each.
    
    In your analysis, go beyond simple keyword matching. Look for underlying themes, transferable skills, and potential areas where the candidate's experience might indirectly apply to the job requirements. Your goal is to present the candidate in the best possible light while maintaining honesty and accuracy.
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
    # Split the output into sections
    sections = re.split(r'\n\n(?=HEADER:|SUMMARY:|COMPARISON:)', output)
    
    # Extract header
    header = re.sub(r'^HEADER:\s*', '', sections[0], flags=re.MULTILINE).strip()
    
    # Extract summary
    summary = re.sub(r'^SUMMARY:\s*', '', sections[1], flags=re.MULTILINE).strip()
    
    # Process comparison
    comparison_raw = re.sub(r'^COMPARISON:\s*', '', sections[2], flags=re.MULTILINE).strip().split('\n')
    your_skills = [item.split('|')[0].strip() for item in comparison_raw if '|' in item]
    job_requirements = [item.split('|')[1].strip() for item in comparison_raw if '|' in item]
    
    return header, summary, (your_skills, job_requirements)
