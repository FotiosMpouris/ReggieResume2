import openai

def analyze_resume_and_job(resume, job_description):
    # Construct the prompt for GPT-4
    prompt = f"""
    Analyze the following resume and job description. Then:
    1. Create a tailored header for the resume.
    2. Write a custom summary highlighting the candidate's most relevant skills and experiences for this job.
    3. Create a two-column comparison of the candidate's skills and the job requirements.

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
    Skill 1|Requirement 1
    Skill 2|Requirement 2
    ...
    """

    # Call GPT-4 API
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert resume tailoring assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract and process the response
    output = response.choices[0].message.content
    header, summary, comparison = process_gpt_output(output)

    return header, summary, comparison

def process_gpt_output(output):
    # Process the GPT output and extract header, summary, and comparison
    # This is a placeholder - you'll need to implement the actual processing logic
    return "Processed Header", "Processed Summary", (["Your Skills"], ["Job Requirements"])
