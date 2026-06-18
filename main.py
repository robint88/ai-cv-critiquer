import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="AI CV Critiquer", page_icon="📃", layout="centered")

st.title("AI CV Critiquer")
st.markdown("Upload your CV in PDF format, and let our AI critique it for you!")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you are applying for (optional)")

analyze = st.button("Analyze CV")

#Function to extract text from PDF files using PyPDF2
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text
#Function to extract text from uploaded file, handling both PDF and plain text formats
def extract_text_from_file(uploaded_file):
    # If the file is a PDF, extract text using PyPDF2, otherwise read it as plain text
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

if analyze and uploaded_file is not None:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("The uploaded file is empty. Please upload a valid CV.")
            st.stop()
        
        prompt = f"""Critique the following CV for the job role '{job_role}'. Focus on the following aspects:
                    1. Content clarity and impact.
                    2. Skills presentation and relevance to the job role.
                    3. Experience description and quantification.
                    4. Specific improvements for {job_role if job_role else 'general job applications'}.

                    CV Content:
                    {file_content}  
                    Provide a detailed critique and actionable feedback to enhance the CV's effectiveness in securing job interviews."""
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an expert career advisor with years specializing in CV critiques."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        st.markdown("### AI Critique Results:")
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")