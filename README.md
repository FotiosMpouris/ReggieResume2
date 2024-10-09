# AI Resume Tailor

AI Resume Tailor is a Streamlit-based web application that uses OpenAI's GPT-4 to analyze resumes and job descriptions, creating tailored resumes and cover letters for job applicants.

## Features

- Resume analysis and tailoring based on job descriptions
- Custom summary generation
- Skills comparison between applicant and job requirements
- Relevant work experience extraction
- Education information summarization
- Cover letter generation
- PDF output for both tailored resume and cover letter

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-resume-tailor.git
   cd ai-resume-tailor
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Create a `.streamlit/secrets.toml` file in the project directory
   - Add your OpenAI API key to the file:
     ```
     openai_api_key = "your-api-key-here"
     ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to the URL provided by Streamlit (usually http://localhost:8501)

3. Paste your resume and the job description into the respective text areas

4. Click "Analyze and Tailor Resume" to generate your tailored resume and cover letter

5. Review the generated content and use the download buttons to save your tailored resume and cover letter as PDFs

## Dependencies

- Python 3.7+
- Streamlit
- OpenAI
- FPDF
- Other dependencies listed in `requirements.txt`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- OpenAI for providing the GPT-4 API
- Streamlit for the web application framework
- FPDF for PDF generation
