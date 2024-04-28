"""
Question_generator.py creates a list of reading comprehension question/answer pairs for a given text file
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Blueprint, request
from docx import Document
import PyPDF2
import time
import tiktoken
import math

question_generator = Blueprint('question_generator', __name__)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY_READSMART")
client = OpenAI(api_key=api_key)


def read_text_from_txt_file(file_path):
    """
    Reads a text file and returns its content as a string.
    """
    with open(file_path, 'r', encoding='utf-8') as scode:
        text = scode.read().replace('\n', '')
    return text


def read_text_from_docx_file(file_path):
    """
    Reads a .docx file and returns its content as a string.
    """
    doc = Document(file_path)
    full_text = ' '.join(paragraph.text for paragraph in doc.paragraphs)
    return full_text


def read_text_from_pdf_file(file_path, start_page, end_page):
    """
    Reads a PDF file and returns the content from the start page to the end page as a string.
    """
    pdf_file_obj = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)

    # Ensure end_page does not exceed the number of pages in the PDF
    end_page = min(end_page, pdf_reader.numPages)

    text = ''
    for page_num in range(start_page-1, end_page+1):  # Python uses 0-based indexing
        page_obj = pdf_reader.getPage(page_num)
        text += page_obj.extractText()

    pdf_file_obj.close()
    return text


def generate_qa_pairs(text, num_questions):
    """
    Generates reading comprehension questions and answers for a given text.
    """

    # Get the tokenizer for the "gpt-4" model
    enc = tiktoken.encoding_for_model("gpt-4")

    # Split the text into chunks of 5000 tokens
    text_chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]

    # Calculate the number of questions per chunk
    num_questions_per_chunk = math.ceil(num_questions / len(text_chunks))

    qa_pairs = []

    for text_chunk in text_chunks:
        # Count the number of tokens in the text chunk and prompt
        text_tokens = len(enc.encode(text_chunk))
        prompt_tokens = len(enc.encode(f"Generate {num_questions_per_chunk} reading comprehension questions and their answers focusing on core ideas/themes. Please format them as follows:\nQuestion Number: Question\nAnswer: Answer\n\nFor example:\nQuestion 1: What is the color of the sky?\nAnswer: The sky is blue.\n\n"))

        total_tokens = text_tokens + prompt_tokens

        # If the total number of tokens exceeds 5000, wait for one minute
        if total_tokens > 5000:
            time.sleep(60)

        # Generate the prompt
        prompt = f"{text_chunk}\n\nGenerate {num_questions_per_chunk} reading comprehension questions and their answers focusing on core ideas/themes. Please format them as follows:\nQuestion Number: Question\nAnswer: Answer\n\nFor example:\nQuestion 1: What is the color of the sky?\nAnswer: The sky is blue.\n\n"

        # Make the API request
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ]
        )

    qa_pairs = []
    for choice in response.choices:
        message = choice.message
        print(f"Processing message with role {message.role} and content\n {message.content}")  # Debug
        if message.role == 'system':
            continue
        elif message.role == 'assistant':
            qa = message.content.split('\n')  # Split the message into separate lines
            for i, line in enumerate(qa):  # Iterate over every line
                if line.startswith('Question'):  # Check if the line is a question
                    print("question recognized")  # debug
                    question = line.split(': ', 1)[1]  # Split on ': ' and take the second part as the question
                elif line.startswith('Answer:'):  # Check if the line is an answer
                    answer = line.split('Answer:', 1)[1]  # Split on 'Answer:' and take the second part as the answer
                    qa_pairs.append((question.strip(), answer.strip()))  # Append the question and answer, removing any leading/trailing whitespace
                    print(f"TEST PAIR;  {qa_pairs}\n")
    print(f"\n\n\n\n\nTHIS IS QA PAIRS;  {qa_pairs}\n")
    return qa_pairs, response


@question_generator.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    textSource = data['text-source']
    numQuestions = data['question-count']

    # Read the text from the file specified by textSource
    text = read_text_from_txt_file(f'generator/{textSource}.txt')

    # Generate the specified number of questions
    qa_pairs, _ = generate_qa_pairs(text, numQuestions)

    return {'qa_pairs': qa_pairs}
