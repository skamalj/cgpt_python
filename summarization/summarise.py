import openai
import flask
from flask import request, jsonify
from flask_cors import CORS,cross_origin
import tiktoken
import os
from math import ceil
import re

# Read the OpenAI API key from the environment variable
openai.api_key = os.environ.get('OPENAPI_API_KEY')
temperature = 0.7
summary_type = None
# Function to generate a summary for a given text chunk
def generate_summary(text_chunk):
    
    # Define the possible summary types and their corresponding prompts
    summary_types = {
        "concise": f"Please provide a concise summary of the given text: {text_chunk}",
        "succinct": f"Could you give me a succinct summary of the provided text: {text_chunk}",
        "comprehensive": f"I'd like a comprehensive and very descriptive summary of the given text: {text_chunk}",
        "elaborate": f"Can you provide an elaborate summary of the provided text: {text_chunk}",
        "detailed": f"Please share a detailed summary of the given text: {text_chunk}",
        "points": f"""Present the summary of following text as a series
        of bullet points or a list of key takeaways,
        which can be more concise and easier to read.: {text_chunk}""",
        "in-depth": f"Could you provide an in-depth summary of the text: {text_chunk}? Please ensure to include all key points and supporting details."
    }
    user_prompt = summary_types.get(summary_type, "Invalid summary type. Please choose from: concise, succinct, comprehensive, elaborate, or detailed.")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """
            You are an intelligent summarizer. Do not truncate input for any reason when creating summaries, use complete text input.
            Adhere to the context provided strictly.
            Do not add any information in the summary which is not in the original text.
            Documents are being provided to you in parts, so it is ok to provide part siummary only. 
            These will eventually be merged and put together to create one simgle summarty.
            """},
            {"role": "user", "content":user_prompt}
        ],
        temperature=temperature,
        stop=None
    )
    summary = response["choices"][0]["message"]["content"]
    summary = re.sub('\s+',' ',summary).strip()
    return summary

# Function to split the document into chunks and generate summary for each chunk
def generate_summaries(document):
    # Calculate the total number of tokens in the document
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    total_tokens = len(encoding.encode(document))

    # Check if the total tokens exceed the model's token limit (keeping some overhead margin)
    model_token_limit = 2500  # Adjust this value based on the model's actual token limit
    if total_tokens > model_token_limit:

        # Calculate the number of chunks based on the desired chunk size
        num_chunks = ceil(total_tokens / (model_token_limit))
        print(f'Number of chunks {num_chunks}')

        # Calculate the number of tokens per chunk
        chars_per_chunk = ceil(len(document) / num_chunks)

        summaries = []
        start_idx = 0
        end_idx = 0

        for i in range(num_chunks):
            # Move to the next chunk
            start_idx = end_idx  if end_idx else 0

            end_idx = min(end_idx + chars_per_chunk, len(document))

            # Generate summary for the current chunk
            chunk_summary = generate_summary(document[start_idx:end_idx])
            summaries.append(chunk_summary)

        # Combine the summaries into a single final summary and then generate the dummary again
        progressive_summary = " ".join(summaries)
        return generate_summaries(progressive_summary)

    else:
        # If total tokens do not exceed the model's limit, generate summary without chunking
        return generate_summary(document)

# Create a Flask app
app = flask.Flask(__name__)

# Define the API endpoint to accept file location, progressive_percentage, and desired_tokens, and return the summary
@app.route('/summarize', methods=['POST'])
@cross_origin()
def summarize_file():
    global temperature
    global summary_type
    # Get the file location, progressive_percentage, and desired_tokens from the request
    file_location = request.json.get('file_location')
    summary_type = request.json.get('summary_type')
    temperature = float(request.json.get('temperature'))
    
    # Read the content of the file
    with open(file_location, 'r') as file:
        document = file.read()
    document = re.sub('\s+',' ',document).strip()
    # Generate the summary using the document content, progressive_percentage, and desired_tokens
    final_summary = generate_summaries(document)

    return jsonify({'summary': final_summary})

if __name__ == '__main__':
    # Run the Flask app on port 5000 (you can change the port if needed)
    app.run(port=5000)
