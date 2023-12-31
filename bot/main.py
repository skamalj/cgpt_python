import openai
from flask import Flask, request, jsonify
from flask_cors import CORS,cross_origin
from bot.care_functions import about_care_insurance, load_care_functions,get_product_summary,product_qna
import os
from math import ceil
import json

# Initialize Flask app
app = Flask(__name__)


def call_openai_model(messages, temperature=0.7,functions=[]):
    if (bool(functions)):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            functions=functions,
            function_call="auto",
            messages=messages,
            temperature=temperature,
            stop=None
        )
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=temperature,
            stop=None
        )

    response_message = response["choices"][0]["message"]

    if response_message.get("function_call"):
        print(response_message["function_call"])
        available_functions = {
            "about_care_insurance": about_care_insurance,
            "get_product_summary": get_product_summary,
            "product_qna": product_qna
        } 
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(function_args) if bool(function_args) else fuction_to_call()
        messages.append(response_message)
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = call_openai_model(messages,temperature)
        return second_response
    print(response["usage"])
    return response["choices"][0]["message"]

# Read the OpenAI API key from the environment variable
openai.api_key = os.environ.get('OPENAI_API_KEY')
temperature = 0.7
# Function to generate a summary for a given text chunk
functions = load_care_functions()

def register_bot_routes(app):
    @app.route('/healthbot', methods=['POST'])
    @cross_origin()
    def healthbot():
            data = request.json

            # Convert the conversationData to the messages format used in call_openai_model
            messages=[
                {"role": "system", "content": """
                You are an assistant working for care insurance organization. You must respond user questions strictly within the context provided, do not add any information outside of context.
                You have been provided with function to aid you with more context when needed. Utilizie this function as your helper.
                Do not make assumption, interview user for further information to get required parameters for functions, for example specifically ask for product name if user does not provide it. Under no circumstance should you assume it.
                If you need more context to answer any question you can utilize provided functions. You do not always have to call functions for answering questions, do make a good judgement on this.
                """},
                #{"role": "user", "content": "What products do you have, list the names?"}
            ]
            for entry in data:
                messages.append({"role": entry['role'], "content": entry['content']})

            # Call the OpenAI model
            response = call_openai_model(messages,temperature,functions)

            return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
