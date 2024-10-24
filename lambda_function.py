import json
import pandas as pd
import boto3
from io import StringIO

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # S3 bucket and file information
    bucket_name = 'project-test1-csv-s3'  # Your S3 bucket name
    file_key = 'traffic_cameras_metadata.csv'  # Your CSV file name in S3

    try:
        # Fetch the CSV file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        csv_content = response['Body'].read().decode('utf-8')

        # Load the CSV content into a pandas DataFrame
        df = pd.read_csv(StringIO(csv_content))

        # Fetch the public video URL from the first row
        stream_url = df.loc[0, 'publicVideoURL']

        # Log the URL
        print(f"Stream URL: {stream_url}")

        return {
            'statusCode': 200,
            'body': json.dumps(f"Stream URL: {stream_url}")
        }
    except Exception as e:
        print(f"Error reading file from S3: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
