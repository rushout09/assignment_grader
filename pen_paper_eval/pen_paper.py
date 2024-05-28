import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
import logging
import gradio as gr
import re

# Import the logger from the main module
logger = logging.getLogger(__name__)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def is_url(string):
    # Regular expression to match URLs
    url_regex = re.compile(
        r'^(https?://)?'  # Optional scheme (http or https)
        r'((([A-Za-z]{1,63}\.)+[A-Za-z]{2,6})|'  # Domain name
        r'((\d{1,3}\.){3}\d{1,3}))'  # or IPv4 address
        r'(:\d+)?'  # Optional port
        r'(/[A-Za-z0-9_\-./]*)?'  # Optional path
        r'(\?[A-Za-z0-9_\-./=&]*)?'  # Optional query
        r'(#\w*)?$'  # Optional fragment
    )

    return re.match(url_regex, string) is not None


def png_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/png;base64,{base64_encoded}"


def convert_to_base_64(file_url: str):
    try:
        with open(file_url, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        logging.info(f"Converted image to base64")
        return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        logging.error(f"An error occurred while converting to base64: {str(e)}", exc_info=e)
        return None


openai_messages = [
    {
        'role': 'system',
        'content': 'You grade assignments. Grade the assignment out of 10. each question contains 5 marks'
    },
    # {
    #     'role': 'user',
    #     "content": [{"type": "text", "text": "Grade the following assignment."},
    #                 {"type": "image_url",
    #                  "image_url": {"url": convert_to_base_64(file_url="")}}]
    # }
]


def qa_bot(message, history):
    files = message.get('files', [])
    text_message = message.get('text')
    for file in files:
        openai_messages.append({"role": "user",
                                "content": [
                                            {
                                                "type": "image_url",
                                                "image_url": {
                                                    "url": png_to_base64(file),
                                                },
                                            }
                                            ]
                                })
    if text_message != '':
        openai_messages.append({"role": "user", "content": text_message})

    response = client.chat.completions.create(
        model='gpt-4o',
        messages=openai_messages,
        max_tokens=500,
        temperature=0.5,
    )

    return response.choices[0].message.content


gr.ChatInterface(qa_bot, multimodal=True).launch(share=True)
