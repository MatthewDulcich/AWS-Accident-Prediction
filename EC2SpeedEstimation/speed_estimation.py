import cv2
from ultralytics.solutions import SpeedEstimator
from pandas import DataFrame
import boto3
from os import remove, system
from datetime import datetime, timedelta

# Get the time of the previous minute (UTC -> ET)
now = datetime.now() - timedelta(hours=5) - timedelta(minutes=1)
yr = now.year
mon = now.month
dy = now.day
hr = now.hour
mn = now.minute

# Choose input and output buckets
input_bucket_name = 'converted-mp4-videos-bucket'
output_bucket_name = 'jfrechmsml650output'
output_bucket_prefix = 'MarylandTrafficCams/'

# List files in video directory
s3 = boto3.client('s3')
files = s3.list_objects(Bucket = input_bucket_name)
files = [i['Key'] for i in files['Contents']]

# List files already in output directory
written_output_files = s3.list_objects(Bucket=output_bucket_name, Prefix=output_bucket_prefix, Delimiter='/')
written_output_files = [i['Key'].split(output_bucket_prefix)[1] for i in written_output_files['Contents'][1:]]
written_output_files = [i.split('_test')[0] for i in written_output_files]

# Get the new files from the previous minute
new_files = [i for i in files if i.split(".")[0] not in written_output_files]
new_files = [i for i in new_files if f'{yr}-{mon:02d}-{dy:02d}_{hr:02d}-{mn:02d}' in i]
if not new_files:
    print(f'No new files to run model. Time: {yr}/{mon:02d}/{dy:02d} {hr:02d}:{mn:02d}:00')
    exit()

# Run analysis on all new files
for file in new_files:
    output_video_file = f"{file.split('.')[0]}_annotated.avi"
    output_csv = f"{file.split('.')[0]}.csv"

    date = file.split('_')[0]
    time = file.split('_')[1]

    file_yr = date.split('-')[0]
    file_mon = date.split('-')[1]
    file_dy = date.split('-')[2]

    file_hr = time.split('-')[0]
    file_min = time.split('-')[1]
    file_sec = time.split('-')[2][:2]

    now = datetime(int(file_yr),int(file_mon),int(file_dy),int(file_hr),int(file_min),int(file_sec))

    s3.download_file(Bucket = input_bucket_name,
                     Key = file,
                     Filename = file)

    # Load video and get width, height, fps
    cap = cv2.VideoCapture(file)
    if not cap.isOpened():
        print(f"Error reading video file: {file}")
        remove(file)
        continue

    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    # initialize writer for output video
    #if not first_run:
    video_writer = cv2.VideoWriter(output_video_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

    # region is [(left,bottom),(right,bottom),(right,top),(left,top)]
    #speed_region = [(int(w/6),int(4*h/5)),(int(5*w/6),int(4*h/5)),(int(5*w/6),int(h/5)),(int(w/6),int(h/5))]
    speed_region = [(int(w/3),int(4*h/5)),(w,int(4*h/5)),(w,int(h/5)),(int(w/3),int(h/5))]
    # Classes: 2 - car, 3 - motorcycle, 5 - bus, 7 - truck
    speed = SpeedEstimator(model="yolo11n.pt", region=speed_region, show=False, classes=[2,3,5,7])

    # Analyze frames of video
    frame_speeds = []
    while cap.isOpened():
        success, im0 = cap.read()

        if success:
            out = speed.estimate_speed(im0)

            # If first run, don't do anything past running data through model
            #if first_run:
            #    continue

            # Get only values not equal to 0 and convert to mph
            # 1 km = 0.621371 mi
            frame_speed = [i * 0.621371 for i in speed.spd.values() if i != 0]
            frame_speeds = frame_speeds + frame_speed

            video_writer.write(im0)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            continue

        print("Video frame is empty or video processing has been successfully completed.")
        break
    cap.release()
    cv2.destroyAllWindows()

    # Get statistics from video...
    # Get count of cars and average traffic speed
    n_cars = len(speed.trkd_ids)

    # Take the average of all speeds computed in video
    if n_cars == 0 or not frame_speeds: # If no cars or no speeds computed
        traffic_speed = -1
    else:
        traffic_speed = (sum(frame_speeds)/len(frame_speeds)).item()

    # Upload output video to s3
    s3.upload_file(output_video_file, output_bucket_name, f'{output_bucket_prefix}{output_video_file}')

    # Create output csv and upload to s3
    # Bridge ID
    output = DataFrame([n_cars,traffic_speed,now,'5a01ab71004500400063d336c4235c0a'],
                       index=['n_cars','traffic_speed','date_time','camera_id']).T
    output.to_csv(output_csv,index=False)
    s3.upload_file(output_csv, output_bucket_name, f'{output_bucket_prefix}{output_csv}')

    # Remove files downloaded locally as they are saved in s3
    remove(file)
    remove(output_video_file)
    remove(output_csv)
