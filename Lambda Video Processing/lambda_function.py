import os
import boto3
import subprocess
from datetime import datetime, timedelta

s3 = boto3.client('s3')

# Specify the new bucket name for .mp4 files
NEW_BUCKET_NAME = 'converted-mp4-videos-bucket'

def lambda_handler(event, context):
    # Get the S3 bucket name and key (uploaded file) from the event
    try:
        source_bucket_name = event['Records'][0]['s3']['bucket']['name']
        ts_file_key = event['Records'][0]['s3']['object']['key']  # Path to the uploaded file
        utc_time_str = event['Records'][0]['eventTime']  # Get the upload timestamp in UTC
    except KeyError as e:
        print(f"Error parsing event structure: {e}")
        return {'statusCode': 400, 'body': 'Invalid event structure'}

    # Convert UTC to ET (Manual Adjustment)
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    et_time = utc_time - timedelta(hours=5)  # Adjusting for ET (Standard Time)
    formatted_time = et_time.strftime("%Y-%m-%d_%H-%M-%S")  # Format time for filename

    # Ensure the file is a .ts file
    if not ts_file_key.endswith('.ts'):
        print(f"Skipping non-.ts file: {ts_file_key}")
        return {'statusCode': 200, 'body': 'File is not a .ts file, skipping'}

    # Generate unique .mp4 filename with ET timestamp
    file_parts = ts_file_key.split("/")[-1].split(".")[0]  # Extract the filename without extension
    mp4_file_key = f"{formatted_time}.mp4"  # Save without folder structure

    # Local paths in Lambda's /tmp directory
    ts_local_path = f"/tmp/{file_parts}.ts"
    mp4_local_path = f"/tmp/{file_parts}.mp4"

    try:
        # Download the .ts file
        s3.download_file(source_bucket_name, ts_file_key, ts_local_path)

        # Convert .ts to .mp4 using ffmpeg
        ffmpeg_cmd = ["/var/task/ffmpeg", "-i", ts_local_path, mp4_local_path]
        result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Check for ffmpeg success
        if result.returncode != 0:
            print(f"FFmpeg error for {ts_file_key}: {result.stderr.decode('utf-8')}")
            return {'statusCode': 500, 'body': f'FFmpeg conversion failed for {ts_file_key}'}

        # Upload the converted .mp4 file to the new S3 bucket
        s3.upload_file(mp4_local_path, NEW_BUCKET_NAME, mp4_file_key)

        # Clean up local files
        os.remove(ts_local_path)
        os.remove(mp4_local_path)

    except Exception as e:
        print(f"Error processing file {ts_file_key}: {e}")
        return {'statusCode': 500, 'body': f'Error processing file {ts_file_key}: {e}'}

    return {'statusCode': 200, 'body': f'File {ts_file_key} converted and uploaded successfully'}
