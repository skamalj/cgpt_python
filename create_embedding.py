import boto3
import json
import time
import openai
from openai.embeddings_utils import get_embedding
import pandas as pd
import os

embedding_model = "text-embedding-ada-002"
# Read the OpenAI API key from the environment variable
openai_api_key = os.environ.get('OPENAPI_API_KEY')
# Set the OpenAI API key
openai.api_key = openai_api_key

def get_complete_response(job_id, textract_client):
    response = textract_client.get_document_text_detection(JobId=job_id)
    next_token = response.get('NextToken')

    while next_token:
        next_response = textract_client.get_document_text_detection(JobId=job_id, NextToken=next_token)
        response['Blocks'].extend(next_response['Blocks'])
        next_token = next_response.get('NextToken')

    return response

def wait_for_job_completion(job_id, textract_client):
    while True:
        response = textract_client.get_document_text_detection(JobId=job_id)
        job_status = response['JobStatus']

        if job_status in ['SUCCEEDED', 'FAILED']:
            break

        print('Job status:', job_status)
        time.sleep(5)  # Wait for 5 seconds before checking again
        complete_response = get_complete_response(job_id, textract_client)

    return complete_response

# send bytes to textract
textract = boto3.client('textract')
response = textract.start_document_text_detection(
    DocumentLocation={
        'S3Object': {
            'Bucket': 'cgpt-skamalj',
            'Name': 'input/kesp102.pdf',
        }
    },
    OutputConfig={
        'S3Bucket': 'cgpt-skamalj',
        'S3Prefix': 'output/kesp102'
    }
)
print(json.dumps(response, indent=4))

response = wait_for_job_completion(response["JobId"], textract)

resp_df = pd.DataFrame(response['Blocks']).query('BlockType == "WORD"').filter(['Text', 'Page'])

resp_df_grouped = resp_df.groupby('Page').agg(lambda x: ' '.join(x))

resp_df_grouped["embedding"] = resp_df_grouped.filter(['Text']).applymap(lambda x: get_embedding(x, engine=embedding_model))

resp_df_grouped.to_csv("kesp102_embedding.csv")
print(resp_df_grouped)

