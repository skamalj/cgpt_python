import pandas
from langchain.tools import tool


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
metric_dict = {
    'first_year_premium':2,
    'num_of_policies':9,
    'lives_covered': 16,
    'sum_assured': 23
}

@tool
def get_data(insurer: str,premium_category: str,metric: str) -> dict:
    """
    This tool provides data for a given insurer and premium category and metric.  
    Before setting insurer name for this function, validate it by calling get_nsurer function first.
    Premium Category is one off the following, select one of these, to pass to the tools, based on user input: Individual Single Premium,Individual Non-Single Premium,Group Single Premium,Group Non-Single Premium,Group Yearly Renewable Premium
    Metrics is one of the following values:'first_year_premium','num_of_policies','lives_covered','sum_assured'.
    Premium category and metric must come from user input, do not assume any value. Ask follow up question to get required value.

    Do not assume any value or input, respond with followup question to get details.
    """
    result = {}  # Create a dictionary to store the result
    metric_col = None
    if metric:
        metric_col = metric_dict[metric]
    df_insurer = df[df['Insurer'] == insurer][df['Category'] == premium_category]
    if metric_col:
        metric_data = df_insurer.iloc[:,metric_col:metric_col + 7]
        result[metric] = metric_data.to_dict(orient='records')
    else:
        for m in metric_dict.keys():
            metric_col = metric_dict[m]
            metric_data = df_insurer.iloc[:, metric_col:metric_col + 7]
            result[m] = metric_data.to_dict(orient='records')
    return {insurer: {premium_category: result}}

@tool
def get_insurers():
    """
    Insurer name provided by user may be partial, you must use this tool to get list of all insurers and select the appropriate one based on user query.
    """
    return df['Insurer'].unique()

# Example usage
#insurer = "Aditya Birla Sun Life"
#premium_category = "Individual Single Premium"
#data = get_data(insurer, premium_category)
#print(data)