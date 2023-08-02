from data_utils import read_json_file, read_text_file
from openai.embeddings_utils import get_embedding, cosine_similarity
import os
import glob
import pandas as pd
import numpy as np

def about_care_insurance():
    return read_text_file('./data/about_care.txt')

def load_care_functions():
    return read_json_file('functions.json')

def get_product_summary(args):
    product_name = args.get("product_name")
    return read_text_file(f'./data/{product_name}.txt')


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

embedding_dfs = read_embeddings_files('./embeddings')

def get_related_text_content(text, embedding_df,product,embedding_model="text-embedding-ada-002"):
    text_embedding = get_embedding(text, engine=embedding_model)
    product_name = f"care-{product}"
    embedding_df = embedding_df.query("name == @product_name")
    
    embedding_df["similarity"] = embedding_df.filter(['embedding']).applymap(lambda x: cosine_similarity(x,text_embedding))

    result_df = embedding_df.sort_values(by=['similarity'], ascending=False)
    print(embedding_df)
    product_match = result_df.iloc[0]["name"]
    top_page = result_df.iloc[0]["Page"]
    print(f"Found match in product {product_match} and page {top_page}")

    content = ''
    for i in range(-1,2):
      try:
        content += ' ' + result_df.query("Page == @top_page+@i").iloc[0].Text
      except Exception:
         pass
    return content

def product_qna(args):
    product_name = args.get("product_name")
    specific_detail_asked = args.get("specific_detail_asked")
    question = args.get("question")
    q = question if question.strip() != "" else f"describe {specific_detail_asked} for this {product_name}"
    return get_related_text_content(q,embedding_df=embedding_dfs,product=product_name)