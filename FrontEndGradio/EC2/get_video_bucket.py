import boto3
import time
from datetime import datetime
# Initialize the S3 client
s3 = boto3.client('s3')

# Bucket and folder details
bucket_name = 'ncongermsml650bucket'
folder_name = 'avi_videos/'
recent_file = None
local_file_path = "./avi_videos/new_video.avi"

def convert_to_seconds(date):

    # Example datetime string and its format
    datetime_format = "%Y-%m-%d %H:%M:%S"
    datetime_str = date.strftime("%Y-%m-%d %H:%M:%S")
    # Parse the string into a datetime object
    dt_object = datetime.strptime(datetime_str, datetime_format)

    # Convert to seconds since epoch
    seconds_since_epoch = dt_object.timestamp()
    return int(seconds_since_epoch)

# Function to check for new .avi files
def check_new_files():
    global recent_file
    get_last_modified = lambda obj: convert_to_seconds(obj['LastModified'])#int(obj['LastModified'].strfti>
    try:
        # List objects in the specified S3 folder
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
        if 'Contents' in response:
            avi_files = [obj['Key'] for obj in sorted(response['Contents'], key = get_last_modified)]
            if avi_files and recent_file == None:
                #get first new file and download into ec2 folder
                print(f"New .avi files found: {avi_files}")
                recent_file = avi_files[-1]
                s3.download_file(bucket_name, recent_file, local_file_path)
            elif avi_files and avi_files[-1] != recent_file:
                print(f"New .avi files found: {avi_files}")
                recent_file = avi_files[-1]
                s3.download_file(bucket_name, recent_file, local_file_path)
            else:
                print("No new .avi files found.")
        else:
            print("No files in the specified folder.")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(1)
