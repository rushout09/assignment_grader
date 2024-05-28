import os
import base64
import json
from dotenv import load_dotenv
from openai import OpenAI
import logging
import csv
import random
import gradio as gr


# Import the logger from the main module
logger = logging.getLogger(__name__)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def get_question():
    csv_file = 'questions.csv'
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        random_row = random.choice(rows)
        formatted_question = (f"Topic: {random_row['Topic']}\nQuestion: {random_row['Question']}\nOptions:\nA) "
                              f"{random_row['Option A']}\nB) {random_row['Option B']}\nC) {random_row['Option C']}\nD) "
                              f"{random_row['Option D']}\nCorrect Option: {random_row['Correct Option']}\nAnswer: "
                              f"{random_row['Answer']}")
        return formatted_question


def convert_to_base_64(file_url: str):
    try:
        with open(file_url, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        logging.info(f"Converted image to base64")
        return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        logging.error(f"An error occurred while converting to base64: {str(e)}", exc_info=e)
        return None


openai_messages = [
    {
        'role': 'system',
        'content': 'You are a Prompt Engineering Professor. You are assessing the technical aptitude of your students.'
                   'Step 1: Use the get_question function to get a question along with options and answer.'
                   'Step 2: Ask the retrieved question to the user.'
                   'Step 3: Let the user know if the answer is correct or not.'
                   'Step 4: Let the user know a track of Total Correct Answers out of Total Questions Asked.'
    },
    # {
    #     'role': 'user',
    #     "content": [{"type": "text", "text": "Grade the following assignment."},
    #                 {"type": "image_url",
    #                  "image_url": {"url": convert_to_base_64(file_url="")}}]
    # }
]
tools = [
        {
            "type": "function",
            "function": {
                "name": "get_question",
                "description": "Get a random question to ask user",
                "parameters": {
                      "type": "object",
                      "properties": {},
                      "required": [],
                },
            },
        }
    ]


def qa_bot(message, history):
    openai_messages.append({
        "content": message,
        "role": "user"
    })
    response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=openai_messages,
            max_tokens=300,
            temperature=0.5,
            tools=tools
    )

    tool_calls = response.choices[0].message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_question": get_question,
        }  # only one function in this example, but you can have multiple
        openai_messages.append(response.choices[0].message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call()
            openai_messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=openai_messages,
            max_tokens=300,
            temperature=0.5,
            tools=tools
        )  # get a new response from the model where it can see the function response

    openai_messages.append({
        "content": response.choices[0].message.content,
        "role": "assistant"
    })
    return response.choices[0].message.content


gr.ChatInterface(qa_bot).launch(share=True)

# Demo:
# Asking and Grading questions with 0 shot learning. Right now. Tuesday.


# Pen and Paper Examination Grading:
# Input Images - 3 image with same questions and diff answers. Grade each image separately. Second Step.
# Extract the roll number and evaluate answers for each roll number. Second Step.

# Automated LLM Based MCQs (Knowledge Testing):
# Asking and Grading questions with RAG. MCQs.


