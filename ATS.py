# import streamlit as st
# import google.generativeai as genai
# import os
# import PyPDF2 as pdf
# from dotenv import load_dotenv
# import json

# load_dotenv() ## load all our environment variables

# genai.configure(api_key="AIzaSyCdX38OjHeF_oHcF2O_YAngAxSzYIwFSps")

# def get_gemini_repsonse(input):
#     model=genai.GenerativeModel('gemini-2.0-flash')
#     response=model.generate_content(input)
#     return response.text

# def input_pdf_text(uploaded_file):
#     reader=pdf.PdfReader(uploaded_file)
#     text=""
#     for page in range(len(reader.pages)):
#         page=reader.pages[page]
#         text+=str(page.extract_text())
#     return text

# #Prompt Template

# input_prompt="""
# Hey Act Like a skilled or very experience ATS(Application Tracking System)
# with a deep understanding of tech field,software engineering,data science ,data analyst
# and big data engineer. Your task is to evaluate the resume based on the given job description.
# You must consider the job market is very competitive and you should provide 
# best assistance for improving thr resumes. Assign the percentage Matching based 
# on Jd and
# the missing keywords with high accuracy
# resume:{text}
# description:{jd}

# I want the response in one single string having the structure
# {{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
# """

# ## streamlit app
# st.title("Smart ATS")
# st.text("Improve Your Resume ATS")
# jd=st.text_area("Paste the Job Description")
# uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please uplaod the pdf")

# submit = st.button("Submit")

# if submit:
#     if uploaded_file is not None:
#         text=input_pdf_text(uploaded_file)
#         print(text)
#         response=get_gemini_repsonse(input_prompt)
#         st.subheader(response)

import streamlit as st
import google.generativeai as genai
import os
import docx2txt
import PyPDF2 as pdf
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Configure the generative AI model with the Google API key
genai.configure(api_key="AIzaSyCdX38OjHeF_oHcF2O_YAngAxSzYIwFSps")

# Set up the model configuration for text generation
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Define safety settings for content generation
safety_settings = [
    {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for category in ["HARASSMENT", "HATE_SPEECH", "SEXUALLY_EXPLICIT", "DANGEROUS_CONTENT"]
]


def generate_response_from_gemini(input_text):
    # Create a GenerativeModel instance with 'gemini-pro' as the model type
    llm = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    # Generate content based on the input text
    output = llm.generate_content(input_text)
    # Return the generated text
    return output.text


def extract_text_from_pdf_file(uploaded_file):
    # Use PdfReader to read the text content from a PDF file
    pdf_reader = pdf.PdfReader(uploaded_file)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += str(page.extract_text())
    return text_content


def extract_text_from_docx_file(uploaded_file):
    # Use docx2txt to extract text from a DOCX file
    return docx2txt.process(uploaded_file)


# Prompt Template
input_prompt_template = """
As an experienced Applicant Tracking System (ATS) analyst,
with profound knowledge in technology, software engineering, data science, 
and big data engineering, your role involves evaluating resumes against job descriptions.
Recognizing the competitive job market, provide top-notch assistance for resume improvement.
Your goal is to analyze the resume against the given job description, 
assign a percentage match based on key criteria, and pinpoint missing keywords accurately.
resume:{text}
description:{job_description}
I want the response in one single string having the structure
{{"Job Description Match":"%","Missing Keywords":"","Candidate Summary":"","Experience":""}}
"""

# Streamlit app
# Initialize Streamlit app
st.title("Enhance Your Resume ATS")
st.markdown('<style>h1{color: white; text-align: center;}</style>', unsafe_allow_html=True)
job_description = st.text_area("Paste the Job Description", height=300)
uploaded_file = st.file_uploader("Upload Your Resume", type=["pdf", "docx"], help="Please upload a PDF or DOCX file")

submit_button = st.button("Submit")

if submit_button:
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf_file(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx_file(uploaded_file)
        
        # Generate the response from the generative AI
        response_text = generate_response_from_gemini(input_prompt_template.format(text=resume_text, job_description=job_description))

        # Extract Job Description Match percentage from the response
        try:
            match_percentage_str = response_text.split('"Job Description Match":"')[1].split('"')[0]
            match_percentage = float(match_percentage_str.rstrip('%'))
        except IndexError:
            match_percentage = 0.0  # In case of an error, assume no match percentage

        # Extract other details from the response
        try:
            missing_keywords = response_text.split('"Missing Keywords":"')[1].split('"')[0]
        except IndexError:
            missing_keywords = "No keywords missing"

        try:
            candidate_summary = response_text.split('"Candidate Summary":"')[1].split('"')[0]
        except IndexError:
            candidate_summary = "No summary available"

        try:
            experience = response_text.split('"Experience":"')[1].split('"')[0]
        except IndexError:
            experience = "No experience information available"

        # Display the results
        st.subheader("ATS Evaluation Result:")

        # Job Description Match
        st.write(f"**Job Description Match**: {match_percentage}%")

        # Missing Keywords
        st.write(f"**Missing Keywords**: {missing_keywords}")

        # Candidate Summary
        st.write(f"**Candidate Summary**: {candidate_summary}")

        # Experience
        st.write(f"**Experience**: {experience}")

        # Display message based on Job Description Match percentage
        if match_percentage >= 80:
            st.text("Move forward with hiring!")
        else:
            st.text("Not a Match.")
