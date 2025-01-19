import boto3
import json
import time
import openai
import pandas as pd
import os
import sys

# Read the input filename from the command line arguments
if len(sys.argv) != 2:
    print("Usage: python script_name.py input_filename.pdf")
    sys.exit(1)

input_filename = sys.argv[1]

embedding_model = "text-embedding-ada-002"
# Read the OpenAI API key from the environment variable
openai_api_key = os.environ.get('OPENAI_API_KEY')
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

# Send bytes to Textract
textract = boto3.client('textract')
response = textract.start_document_text_detection(
    DocumentLocation={
        'S3Object': {
            'Bucket': 'cgpt-skamalj-sso',
            'Name': f'input/{input_filename}',
        }
    },
    OutputConfig={
        'S3Bucket': 'cgpt-skamalj-sso',
        'S3Prefix': f'output/{input_filename[:-4]}'
    }
)
print(json.dumps(response, indent=4))

response = wait_for_job_completion(response["JobId"], textract)

# Extract text and page numbers
resp_df = pd.DataFrame(response['Blocks']).query('BlockType == "WORD"').filter(['Text', 'Page'])

# Group words by page
resp_df_grouped = resp_df.groupby('Page').agg(lambda x: ' '.join(x))

# Embed the grouped text using the new OpenAI SDK
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model=embedding_model
    )
    return response['data'][0]['embedding']

# Apply embedding to the grouped text
#resp_df_grouped["embedding"] = resp_df_grouped["Text"].apply(get_embedding)

# Save the embedding and text to output files
output_embedding_filename = f'{input_filename[:-4]}_embedding.csv'
output_text_filename = f'{input_filename[:-4]}.txt'

# Save the embeddings to a CSV file
#resp_df_grouped['embedding'].to_csv(output_embedding_filename, header=False, index=False)

# Save the plain text to a .txt file
file_text = pd.Series(resp_df_grouped['Text']).str.cat(sep=' ')
pd.DataFrame([file_text]).to_csv(output_text_filename, header=False, index=False)

print(resp_df_grouped)
