import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
import os
from flask_cors import CORS,cross_origin

app = Flask(__name__)
CORS(app)

def get_response(text):
    embedding_model = "text-embedding-ada-002"

    # Read the OpenAI API key from the environment variable
    openai_api_key = os.environ.get('OPENAPI_API_KEY')
    # Set the OpenAI API key
    openai.api_key = openai_api_key

    df_ch1 = pd.read_csv('kesp101_embedding.csv')
    df_ch1['name'] = 'Horses'
    df_ch2 = pd.read_csv('kesp102_embedding.csv')
    df_ch2['name'] = 'Address'

    resp_df_grouped = pd.concat([df_ch1, df_ch2])

    resp_df_grouped['embedding'] = resp_df_grouped.embedding.apply(eval).apply(np.array)

    test_embedding = get_embedding(text, engine=embedding_model)

    resp_df_grouped["similarity"] = resp_df_grouped.filter(['embedding']).applymap(lambda x: cosine_similarity(x,test_embedding))

    resp_df_grouped_result = resp_df_grouped.sort_values(by=['similarity'], ascending=False)

    chapter = resp_df_grouped_result.iloc[0]["name"]
    top_page = resp_df_grouped_result.iloc[0].Page
    print(f"Found match in chapter {chapter} and page {top_page}")

    content = ''
    for i in range(-1,2):
      try:
        content += ' ' + resp_df_grouped_result.query("name == @chapter").query("Page == @top_page+@i").iloc[0].Text
      except Exception:
         pass
 
    response_message = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.7,
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
    print(data)
    response = get_response(text)
    return jsonify({'response': response})

if __name__ == '__main__':
    # Run the server
    app.run(host='0.0.0.0', port=5000)
