
import boto3
import datetime
import pandas as pd
import time
# Initialize the S3 client
s3 = boto3.client('s3')
local_file_path = 'predictions.csv'

def check_file_updated(bucket_name, file_key, last_known_update):
    response = s3.head_object(Bucket=bucket_name, Key=file_key)
    last_modified = response['LastModified']

    if last_modified > last_known_update:
        #print("The file has been updated.")
        #Pull the new file into EC2 instance and modify master.csv
        s3.download_file(bucket_name, file_key, local_file_path)
        new_data = pd.read_csv(file_key)
        master_data = pd.read_csv('master.csv')
        concat_data = pd.concat([master_data,new_data], axis=0)

        #Write newly created appended data to master doc
        concat_data.to_csv("master.csv", index=False)
        return last_modified
    else:
        return last_known_update

def main():
    # Replace with your bucket name and file key
    bucket_name = 'dulcichmsml650bucket'
    file_key = 'predictions.csv'

    # Set the last known update time (use datetime.datetime)
    last_known_update = datetime.datetime(2024,11,1,0,0,0, tzinfo=datetime.timezone.utc)
    while True:
        # Check if the file has been updated
        last_known_update = check_file_updated(bucket_name, file_key, last_known_update)
        time.sleep(1)
