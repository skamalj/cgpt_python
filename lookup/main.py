import pandas
from langchain.agents import tool

def load_data(file):
    df = pandas.read_excel(file,header=2,index_col=None, sheet_name=2, skipfooter=3)
    df = df.rename(columns={'Unnamed: 1':'Category', 'Unnamed: 0':'Sno'})
    df = df[df['Category'].notna()]
    df = df.reset_index(drop=True)
    insurer_indexes = df[df['Sno'].notna()].index
    for i in range(len(insurer_indexes)):
        df.loc[insurer_indexes[i]:insurer_indexes[i]+5,'Insurer']  = df.filter(['Category']).iloc[[insurer_indexes[i]]].values[0][0]
    df = df[df['Insurer'].notna()]
    return df

df = load_data('policy.xlsx')
metric = {
    'First Year Premium':2,
    'num_of_policies':9,
    'lives_covered': 16,
    'sum_assured': 23
}

@tool
def get_data(insurer,premium_category,metric=None, dimension=None):
    metric_col = metric[metric] if metric.notna() else None
    df_insurer = df[df['Insurer'] == insurer][df['Category'] == premium_category]
    if metric_col:
        df_insurer = df_insurer.iloc[:,metric_col:metric_col + 7]
    if dimension:
        df_insurer = df_insurer.filter(['For july, 2022'])
    return df_insurer.to_json()

@tool
def get_insurers():
    return df['Insurer'].unique()

print(get_insurers())