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

def get_related_text_content(text, embedding_df,product,head,embedding_model="text-embedding-ada-002"):
    text_embedding = get_embedding(text, engine=embedding_model)
    product_name = f"care-{product}"
    if product != 'all':
        embedding_df = embedding_df.query("name == @product_name")
    
    embedding_df["similarity"] = embedding_df.filter(['embedding']).applymap(lambda x: cosine_similarity(x,text_embedding))

    result_df = embedding_df.sort_values(by=['similarity'], ascending=False).head(head)
    print(result_df)
    content = pd.Series(result_df['Text']).str.cat(sep=' ')
    return content

def product_qna(args):
    product_names = args.get("product_names")
    specific_focus = args.get("specific_focus")
    user_input = args.get("user_input")

    if product_names is None or (product_names == 'all' and specific_focus == 'summary') :
        return about_care_insurance()

    product_list = product_names.split(',')

    content =''
    head = 4 if len(product_list) > 1 else 10
    for p in product_list:
        content += f'{p.strip()}\n'
        content += f'{get_related_text_content(user_input,embedding_df=embedding_dfs,product=p.strip(),head=head)}\n\n'
    
    return content