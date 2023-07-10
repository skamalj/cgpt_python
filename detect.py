import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
import pandas as pd
import numpy as np
import os

test_question = "why was girl looking for mothers belongings"
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

print(resp_df_grouped)

test_embedding = get_embedding(test_question, engine=embedding_model)

resp_df_grouped["similarity"] = resp_df_grouped.filter(['embedding']).applymap(lambda x: cosine_similarity(x,test_embedding))

resp_df_grouped_result = resp_df_grouped.sort_values(by=['similarity'], ascending=False)
print(resp_df_grouped_result)

chapter = resp_df_grouped_result.iloc[0].name
top_page = resp_df_grouped_result.iloc[0].Page


page1 = resp_df_grouped_result.query("name == @chapter").query("Page == @top_page-2").Text
page2 = resp_df_grouped_result.query("name == @chapter").query("Page == @top_page-1").Text
page3 = resp_df_grouped_result.iloc[0].Text
page4 = resp_df_grouped_result.query("name == @chapter").query("Page == @top_page+1").Text
page5 = resp_df_grouped_result.query("name == @chapter").query("Page == @top_page+2").Text
print(resp_df_grouped_result.query("name == @chapter"))
response_message = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "assistant", "content": f"{page1} {page2} {page3} {page4} {page5}"},
        {"role": "user", "content": test_question}
    ]
)

print(response_message["choices"][0]["message"])