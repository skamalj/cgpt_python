import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
import os
from flask_cors import CORS,cross_origin
import traceback
import tiktoken

app = Flask(__name__)
CORS(app)
embedding_model = "text-embedding-ada-002"

def load_embeddings():
    filenames = [
        ('kesp101_embedding.csv', 'Horses'),
        ('kesp102_embedding.csv', 'Address'),
        ('kesp103_embedding.csv', 'Mother'),
        ('kesp104_embedding.csv', 'Ghat'),
        ('kesp105_embedding.csv', 'Birth'),
        ('kesp106_embedding.csv', 'Melon')
    ]
    
    dfs = []
    for filename, name in filenames:
        df = pd.read_csv(filename)
        df['name'] = name
        df['embedding'] = df['embedding'].apply(eval).apply(np.array)
        dfs.append(df)
    
    return pd.concat(dfs)

# Load embeddings
embedding_df = load_embeddings()

def get_related_text_content(text):
    text_embedding = get_embedding(text, engine=embedding_model)

    embedding_df["similarity"] = embedding_df.filter(['embedding']).applymap(lambda x: cosine_similarity(x,text_embedding))

    result_df = embedding_df.sort_values(by=['similarity'], ascending=False)

    chapter = result_df.iloc[0]["name"]
    top_page = result_df.iloc[0]["Page"]
    print(f"Found match in chapter {chapter} and page {top_page}")

    content = ''
    for i in range(-1,2):
      try:
        content += ' ' + result_df.query("name == @chapter").query("Page == @top_page+@i").iloc[0].Text
      except Exception:
         pass
    return content

def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(encoding.encode(text))
    return num_tokens

def get_response(text, temperature, full='N'):
    

    # Read the OpenAI API key from the environment variable
    openai_api_key = os.environ.get('OPENAPI_API_KEY')
    # Set the OpenAI API key
    openai.api_key = openai_api_key

    content =  get_related_text_content(text) if full == 'N' else ' '.join(embedding_df['Text'])
    print(f'Request has {count_tokens(content + text)} tokens')

    response_message = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": content},
            {"role": "user", "content": text}
        ]
    )

    return response_message["choices"][0]["message"]

@app.route('/query', methods=['POST'])
@cross_origin()
def query():
    data = request.get_json()
    text = data['text']
    full_content = 'Y' if data['full'] else 'N'
    temperature = float(data['temperature'])
    print(data)
    
    try:
        response = get_response(text, temperature, full_content)
    except Exception as e:
        print(traceback.format_exc() )
        response = {'error': str(e)}
    
    return jsonify({'response': response})

if __name__ == '__main__':
    # Run the server
    app.run(host='0.0.0.0', port=5000)
