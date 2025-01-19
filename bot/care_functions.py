import os
import glob
import pandas as pd
import numpy as np
import openai
from bot.data_utils import read_json_file, read_text_file

def about_care_insurance():
    return read_text_file('./bot/data/about_care.txt')

def load_care_functions():
    return read_json_file('./bot/functions.json')

def get_product_summary(args):
    product_name = args.get("product_name")
    return read_text_file(f'./bot/data/{product_name}.txt')

def read_embeddings_files(directory_path):
    dfs = []
    filenames = glob.glob(os.path.join(directory_path, "*_embedding.csv"))
    print(filenames)
    
    for filename in filenames:
        name = os.path.basename(filename).split("_embedding.csv")[0]
        df = pd.read_csv(filename)
        df['name'] = name
        df['embedding'] = df['embedding'].apply(eval).apply(np.array)
        dfs.append(df)
    
    return pd.concat(dfs)

embedding_dfs = read_embeddings_files('./bot/embeddings')

# Define cosine similarity if not available in the new SDK
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Updated function to get related text content
def get_related_text_content(text, embedding_df, product, head=3, embedding_model="text-embedding-ada-002"):
    # Fetch the embedding for the input text
    response = openai.Embedding.create(
        input=text,
        model=embedding_model
    )
    text_embedding = np.array(response['data'][0]['embedding'])

    product_name = f"care-{product}"
    if product != 'all':
        embedding_df = embedding_df.query("name == @product_name")
    
    embedding_df["similarity"] = embedding_df['embedding'].apply(lambda x: cosine_similarity(x, text_embedding))

    result_df = embedding_df.sort_values(by=['similarity'], ascending=False).head(head)
    print(result_df)
    content = pd.Series(result_df['Text']).str.cat(sep=' ')
    return content

def product_qna(args):
    product_names = args.get("product_names")
    specific_focus = args.get("specific_focus")
    user_input = args.get("user_input")

    if product_names is None or (product_names == 'all' and specific_focus == 'summary'):
        return about_care_insurance()
    prompt = ''
    if product_names == "all":
        product_names = "saksham,supreme,heart"
    for product_name in product_names.split(","):
        prompt += f"{product_name.strip()}\n"
        prompt += get_related_text_content(user_input, embedding_df=embedding_dfs, product=product_name.strip())
        prompt += "\n\n"

    return get_related_text_content(user_input, embedding_df=embedding_dfs, product=product_name)
