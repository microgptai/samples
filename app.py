import streamlit as st
import requests
import tempfile
import os
from pdfminer.high_level import extract_text
import openai

# Ensure the OpenAI key is correctly set in your environment
def get_openai_api_key():
    return os.getenv("OPENAI_API_KEY")

# Convert PDF file to text
def convert_pdf_to_text(file_path):
    """ Convert PDF file to text using pdfminer.six. """
    return extract_text(file_path)

# Use OpenAI's GPT-3 to generate answers
def ask_question(texts, question):
    """ Generate answers using OpenAI's GPT-3 based on the provided texts. """
    api_key = get_openai_api_key()
    openai.api_key = api_key

    # Combine all texts into a single string for processing
    combined_texts = "\n\n".join(texts)

    # Format for chat-based model
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Question: {question}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150
    )
    return response['choices'][0]['message']['content']

# Streamlit UI setup
st.title('Multi-Document Analysis Engine')
st.subheader('Upload PDFs or enter URLs for analysis:')
uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
urls = st.text_area("Enter PDF URLs, separated by new lines:")

texts = []

# Process uploaded files
if uploaded_files:
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            extracted_text = convert_pdf_to_text(tmp_file.name)
            texts.append(extracted_text)

# Process URLs
if urls:
    for url in urls.split():
        response = requests.get(url)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(response.content)
                extracted_text = convert_pdf_to_text(tmp_file.name)
                texts.append(extracted_text)

# Interaction for processing documents
if st.button('Process Documents'):
    if texts:
        st.success('Documents processed successfully!')
    else:
        st.error('No documents were processed.')

# Interaction for asking a question
question = st.text_input("Ask a question based on the loaded documents:")
if question and texts:
    answer = ask_question(texts, question)
    st.write("Answer:", answer)
else:
    st.write("Please load some documents and enter a question.")

