import streamlit as st
import openai
from fpdf import FPDF
import PyPDF2

openai.api_key = st.secrets['OPENAI_API_KEY']

def gpt_generate_summary(input_text):
    res = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for text summarization for a legal professional.",
            },
            {
                "role": "user",
                "content": f"Summarize this legal document to make it brief, concise, and comprehensible for laymen.: {input_text}",
            },
        ],
    )
    return res.choices[0].message.content

def txt_to_pdf(summary_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=summary_text)
    with st.spinner("Creating PDF..."):
        pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes

def pdf_to_text(pdf_bytes):
    pdf_reader = PyPDF2.PdfReader(pdf_bytes)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

def process_file(input_text):
    input_text = ""
    file_type = input_file.name.split(".")[-1].lower()
    if file_type == "txt":
        input_text = input_file.getvalue().decode("utf-8")
    elif file_type == "pdf":
        input_text = pdf_to_text(input_file)
    else:
        st.error("Unsupported file format. Please upload a TXT or PDF file.")
        st.stop()
    
    st.write("#### Original Document")
    with st.expander("See full text"):
        st.write(input_text)

    final_summary = gpt_generate_summary(input_text)
    output_pdf = txt_to_pdf(final_summary)

    st.write("#### Summarized Document")
    with st.expander("See full text"):
        st.write(final_summary)

    st.download_button(
        label="Download Summary as PDF",
        data=output_pdf,
        file_name="output.pdf",
        mime="application/pdf",
    )

st.title("LegalSynth: Legal Doc Summarizer")

# Input File Section
input_file = st.file_uploader("Upload Legal Document (TXT or PDF format)", type=["txt", "pdf"])

if input_file:
    process_file(input_file)
